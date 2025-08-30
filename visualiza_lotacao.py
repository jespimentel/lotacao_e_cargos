import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Cargos por Lotação (Julho de 2025)",
    page_icon="📊",
    layout="wide"
)

# --- Funções ---

@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega os dados de um arquivo CSV, com cache para otimização.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        # Garante que as colunas principais não tenham valores nulos que possam causar erros
        df.dropna(subset=['Lotação', 'Cargo', 'Nome'], inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado. Certifique-se de que ele está na mesma pasta que o script.")
        return None

# --- Título e Descrição ---
st.title("📊 Cargos por Lotação")
st.markdown("""
Utilize os filtros ao lado para selecionar as lotações e respectivos cargos.
""")

# --- Carregamento dos Dados ---
# Substitua 'servidores-ativos-remuneracao-07-2025.csv' pelo nome do seu arquivo se for diferente
df = carregar_dados('servidores-ativos-remuneracao-07-2025.csv')

if df is not None:
    # --- Barra Lateral com Filtros ---
    st.sidebar.header("Filtros")

    # Obter listas únicas e ordenadas para os filtros
    lista_lotacoes = sorted(df['Lotação'].unique())
    lista_cargos = sorted(df['Cargo'].unique())

    # Filtro de Lotação com multiselect e limite de 5
    lotacoes_selecionadas = st.sidebar.multiselect(
        "Selecione a(s) Lotação(ões) (máx. 5):",
        options=lista_lotacoes,
        default=['SERVICO TECNICO-ADMINISTRATIVO DE PIRACICABA'], # Nenhuma lotação selecionada por padrão
        help="Escolha até 5 lotações para comparar."
    )
    
    # Filtro de Cargo
    cargos_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Cargo(s):",
        options=lista_cargos,
        default=lista_cargos,
        help="Escolha um ou mais cargos. Se nenhum for selecionado, todos serão exibidos."
    )
    
    # --- Lógica de Exibição Principal e Validação ---
    if len(lotacoes_selecionadas) > 5:
        st.sidebar.error("Limite excedido! Selecione até 5 lotações.")
        st.error("### Por favor, desmarque algumas lotações para continuar.")
    
    elif not lotacoes_selecionadas:
        st.info("⬅️ Selecione ao menos uma lotação na barra lateral para visualizar os dados.")

    else:
        lotacoes_a_filtrar = lotacoes_selecionadas
        
        # Se a lista de cargos estiver vazia, considera como "todos"
        if not cargos_selecionados:
            cargos_a_filtrar = lista_cargos
        else:
            cargos_a_filtrar = cargos_selecionados

        # --- Filtragem dos Dados ---
        df_filtrado = df[
            df['Lotação'].isin(lotacoes_a_filtrar) &
            df['Cargo'].isin(cargos_a_filtrar)
        ]

        # --- Processamento e Visualização ---
        if not df_filtrado.empty:
            st.header("Distribuição de Cargos por Lotação")

            # Agrupar dados para o gráfico, contando servidores e agregando nomes para o hover
            df_grafico = df_filtrado.groupby(['Lotação', 'Cargo']).agg(
                Quantidade=('Nome', 'count'),
                Servidores=('Nome', lambda nomes: ', '.join(nomes))
            ).reset_index()

            # Criar o gráfico de barras com Plotly
            fig = px.bar(
                df_grafico,
                x='Lotação',
                y='Quantidade',
                color='Cargo',
                title='Quantidade de Servidores por Cargo em cada Lotação',
                labels={
                    'Quantidade': 'Nº de Servidores',
                    'Lotação': 'Lotação',
                    'Cargo': 'Cargo'
                },
                hover_name='Cargo',
                hover_data={
                    'Lotação': True,
                    'Quantidade': True,
                    'Cargo': False, # Oculta o cargo do hover data padrão pois já está no hover_name
                    'Servidores': True
                },
                text_auto=True,
                barmode='stack' # Empilha as barras para melhor visualização
            )

            # Melhorias no layout do gráfico
            fig.update_layout(
                xaxis_tickangle=-45,
                xaxis={'categoryorder':'total descending'},
                legend_title_text='Cargos',
                uniformtext_minsize=8, 
                uniformtext_mode='hide'
            )
            
            # Exibir o gráfico
            st.plotly_chart(fig, use_container_width=True)

            # --- Exibição dos Dados em Tabela ---
            with st.expander("Visualizar dados filtrados em tabela"):
                st.dataframe(df_filtrado)

        else:

            st.warning("Nenhum dado encontrado para os filtros selecionados.")
