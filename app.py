import streamlit as st
import sqlite3
import pandas as pd

# Função para conectar ao banco de dados
def get_connection():
    conn = sqlite3.connect('football_fixtures.db')
    return conn

# Função para obter os dados das partidas
def get_fixtures():
    conn = get_connection()
    query = '''
    SELECT f.id, l.name AS league_name, l.logo AS league_logo, ht.name AS home_team, ht.logo AS home_logo, 
           at.name AS away_team, at.logo AS away_logo, f.date, f.status, f.home_score, f.away_score
    FROM fixtures f
    JOIN league l ON f.league_id = l.id
    JOIN teams ht ON f.home_team_id = ht.id
    JOIN teams at ON f.away_team_id = at.id
    '''
    fixtures = pd.read_sql(query, conn)
    conn.close()
    return fixtures

# Configuração do Streamlit
st.title('Dados das Partidas de Futebol')
st.write('Este aplicativo exibe dados das partidas armazenadas no banco de dados SQLite.')

# Obter os dados das partidas
fixtures_data = get_fixtures()

# Criar abas
tab1, tab2 = st.tabs(["Lista de Partidas", "Detalhes da Partida"])

# Aba 1: Lista de Partidas
with tab1:
    st.subheader('Lista de Partidas')
    if not fixtures_data.empty:
        # Exibir apenas as colunas relevantes, removendo a coluna 'status'
        fixtures_display = fixtures_data[['home_team', 'away_team', 'date', 'league_logo']]
        fixtures_display.columns = ['Time da Casa', 'Time Visitante', 'Data', 'Logo da Liga']
        
        # Adicionar colunas de imagem
        for i, row in fixtures_display.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.image(row['Logo da Liga'], width=50)  # Imagem do logo da liga
            with col2:
                st.write(f"{row['Time da Casa']} vs {row['Time Visitante']}")  # Exibe o confronto
            with col3:
                st.write(row['Data'])  # Exibe a data
    else:
        st.write('Nenhum dado encontrado.')

# Aba 2: Detalhes da Partida
with tab2:
    st.subheader('Detalhes da Partida')
    if not fixtures_data.empty:
        # Exibir seleção com nomes dos times sem a data
        fixture_options = fixtures_data.apply(lambda row: f"{row['home_team']} vs {row['away_team']}", axis=1)
        fixture_selection = st.selectbox('Selecione uma partida para ver detalhes:', fixture_options)

        # Obter o ID da partida correspondente à seleção
        selected_fixture_id = fixtures_data.loc[fixtures_data.apply(lambda row: f"{row['home_team']} vs {row['away_team']}" == fixture_selection, axis=1), 'id'].values[0]
        
        # Filtrar os dados da partida selecionada
        selected_fixture = fixtures_data[fixtures_data['id'] == selected_fixture_id]
        
        # Renomear colunas para exibição
        selected_fixture.columns = ['ID', 'Liga', 'Logo da Liga', 'Time da Casa', 'Logo Casa', 'Time Visitante', 'Logo Visitante', 'Data', 'Status', 'Gols da Casa', 'Gols do Visitante']
        
        # Exibir logos dos times
        col1, col2 = st.columns(2)
        with col1:
            st.image(selected_fixture['Logo Casa'].values[0], width=100)  # Imagem do logo do time da casa
            st.write(f"{selected_fixture['Time da Casa'].values[0]} - {selected_fixture['Gols da Casa'].values[0]} Gols")
        with col2:
            st.image(selected_fixture['Logo Visitante'].values[0], width=100)  # Imagem do logo do time visitante
            st.write(f"{selected_fixture['Time Visitante'].values[0]} - {selected_fixture['Gols do Visitante'].values[0]} Gols")

        # Exibir dados da partida
        st.write("### Detalhes da Partida")
        st.write(f"Liga: {selected_fixture['Liga'].values[0]}")
        st.write(f"Data: {selected_fixture['Data'].values[0]}")
    else:
        st.write("Nenhuma partida disponível para seleção.")
