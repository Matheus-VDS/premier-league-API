import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Dashboard Premier League", page_icon="⚽", layout="wide")

# Título e introdução
st.title("🏆 Dashboard da Premier League")

# Funções para conectar ao banco de dados e obter dados (já existentes)
def get_fixtures_connection():
    return sqlite3.connect('football_fixtures.db')

def get_statistics_connection():
    return sqlite3.connect('football_statistics.db')

def get_fixtures_data():
    conn = get_fixtures_connection()
    query = '''
    SELECT f.id, l.name AS league_name, ht.name AS home_team, ht.logo AS home_logo,
           at.name AS away_team, at.logo AS away_logo, f.date, f.status,
           f.home_score AS home_goals, f.away_score AS away_goals
    FROM fixtures f
    JOIN league l ON f.league_id = l.id
    JOIN teams ht ON f.home_team_id = ht.id
    JOIN teams at ON f.away_team_id = at.id
    '''
    fixtures_data = pd.read_sql(query, conn)
    conn.close()
    return fixtures_data

def get_statistics_data():
    conn = get_statistics_connection()
    goals_data = pd.read_sql("SELECT * FROM goals", conn)
    fixtures_data = pd.read_sql("SELECT * FROM fixtures", conn)
    clean_sheet_data = pd.read_sql("SELECT * FROM clean_sheet", conn)
    penalty_data = pd.read_sql("SELECT * FROM penalty", conn)
    conn.close()
    return goals_data, fixtures_data, clean_sheet_data, penalty_data

# Configuração do título e menu lateral
menu_options = ["Página Inicial", "Lista de Partidas", "Detalhes da Partida", "Gráficos de Estatísticas"]
choice = st.sidebar.selectbox("Seções", menu_options)

# Página Inicial
if choice == "Página Inicial":

    st.subheader("Este é um site que mostra algumas visualizações de dados e estatísticas"
             " das partidas de futebol do campeonato inglês Premier League!")

# Lista de Partidas
elif choice == "Lista de Partidas":
    st.header('Lista de Partidas')
    fixtures_data = get_fixtures_data()
    if not fixtures_data.empty:
        for index, row in fixtures_data.iterrows():
            match_date = pd.to_datetime(row['date']).strftime('%d/%m/%Y %H:%M')
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if pd.notnull(row['home_logo']):
                        st.image(row['home_logo'], width=60)
                    st.write(f"**{row['home_team']}**")
                with col2:
                    st.markdown("<h4 style='text-align: center;'>🆚</h4>", unsafe_allow_html=True)
                    st.write(f"Data: **{match_date}**")
                with col3:
                    if pd.notnull(row['away_logo']):
                        st.image(row['away_logo'], width=60)
                    st.write(f"**{row['away_team']}**")
                st.markdown("---")
    else:
        st.write("Nenhum dado encontrado.")

# Detalhes da Partida
elif choice == "Detalhes da Partida":
    st.header('Detalhes da Partida')
    
    # Obtenha os dados das partidas
    fixtures_data = get_fixtures_data()

    # Obtenha a lista de times do banco de dados a partir da tabela 'teams'
    teams_data = fixtures_data['home_team'].unique().tolist() + fixtures_data['away_team'].unique().tolist()
    teams_data = list(set(teams_data))  # Remover duplicatas

    # Seletor para escolher um time
    selected_team = st.selectbox("Escolha um time", teams_data)
    
    # Filtra as partidas para o time selecionado
    team_fixtures = fixtures_data[(fixtures_data['home_team'] == selected_team) | (fixtures_data['away_team'] == selected_team)]
    
    if not team_fixtures.empty:
        fixture_options = team_fixtures.apply(lambda row: f"{row['home_team']} vs {row['away_team']} em {row['date']}", axis=1)
        fixture_selection = st.selectbox('Selecione uma partida para ver detalhes:', fixture_options)

        selected_fixture_id = team_fixtures.loc[team_fixtures.apply(lambda row: f"{row['home_team']} vs {row['away_team']} em {row['date']}" == fixture_selection, axis=1), 'id'].values[0]
        selected_fixture = team_fixtures[team_fixtures['id'] == selected_fixture_id]
        home_goals = selected_fixture['home_goals'].values[0]
        away_goals = selected_fixture['away_goals'].values[0]
        
        # Verifica se a partida ainda vai acontecer
        match_date = pd.to_datetime(selected_fixture['date'].values[0]).tz_localize(None)  # Remover a informação de fuso horário
        if match_date > pd.to_datetime("now").tz_localize(None):  # Remover a informação de fuso horário
            st.write("Esta partida ainda vai acontecer.")
        else:
            if home_goals > away_goals:
                winner_team = selected_fixture['home_team'].values[0]
            elif away_goals > home_goals:
                winner_team = selected_fixture['away_team'].values[0]
            else:
                winner_team = "Empate"

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.image(selected_fixture['home_logo'].values[0], width=80)
                st.write(f"**{selected_fixture['home_team'].values[0]}**")
                st.markdown(f"Gols: <span style='color: white;'>{int(home_goals)}</span>", unsafe_allow_html=True)  # Exibe apenas o inteiro
            with col2:
                st.markdown("<h1 style='text-align: center;'>🆚</h1>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center;'>{int(home_goals)} - {int(away_goals)}</h1>", unsafe_allow_html=True)  # Exibe apenas o inteiro
            with col3:
                st.image(selected_fixture['away_logo'].values[0], width=80)
                st.write(f"**{selected_fixture['away_team'].values[0]}**")
                st.markdown(f"Gols: <span style='color: white;'>{int(away_goals)}</span>", unsafe_allow_html=True)  # Exibe apenas o inteiro
            st.markdown(f"<h2 style='text-align: center; color: green;'>Vencedor: {winner_team}</h2>", unsafe_allow_html=True)
    else:
        st.write("Nenhuma partida disponível para o time selecionado.")

# Gráficos de Estatísticas
elif choice == "Gráficos de Estatísticas":
    st.header('Gráficos de Estatísticas')
    fixtures_data = get_fixtures_data()  # Obtém os dados das partidas

    if not fixtures_data.empty:
        # Gráfico de resultados das partidas (Vitórias, Empates e Derrotas)
        results = {
            'Vitórias': fixtures_data[fixtures_data['home_goals'] > fixtures_data['away_goals']].shape[0] + fixtures_data[fixtures_data['away_goals'] > fixtures_data['home_goals']].shape[0],
            'Empates': fixtures_data[fixtures_data['home_goals'] == fixtures_data['away_goals']].shape[0]
        }

        fig_results = px.bar(
            x=list(results.keys()),
            y=list(results.values()),
            labels={'x': 'Resultado', 'y': 'Número de Jogos'},
            title="Vitórias, Empates",
            color=list(results.keys()),
            color_discrete_sequence=px.colors.sequential.Bluyl  # Cores sequenciais
        )
        
        for i, value in enumerate(results.values()):
            fig_results.add_annotation(x=list(results.keys())[i], y=value, text=str(value), showarrow=True, arrowhead=2)
        st.plotly_chart(fig_results)

        # Gráfico de Gols em Casa vs Fora
        goals_home = fixtures_data['home_goals'].mean()
        goals_away = fixtures_data['away_goals'].mean()

        fig_goals_avg = px.bar(
            x=['Média Casa', 'Média Fora'],
            y=[goals_home, goals_away],
            labels={'x': 'Tipo de Jogo', 'y': 'Número Médio de Gols'},
            title="Média de Gols em Casa e Fora",
            color=['Média Casa', 'Média Fora'],
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        for i, value in enumerate([goals_home, goals_away]):
            fig_goals_avg.add_annotation(x=['Média Casa', 'Média Fora'][i], y=value, text=f"{value:.2f}", showarrow=True, arrowhead=2)
        st.plotly_chart(fig_goals_avg)

        # Gráfico de Distribuição de Gols por Partida
        fig_goals_distribution = px.scatter(
            fixtures_data,
            x='home_goals',
            y='away_goals',
            title='Distribuição de Gols por Partida',
            labels={'home_goals': 'Gols em Casa', 'away_goals': 'Gols Fora'},
            trendline='ols'  # Adiciona uma linha de tendência
        )
        st.plotly_chart(fig_goals_distribution)

        # Gols Totais por Time
        goals_by_team_home = fixtures_data.groupby('home_team')['home_goals'].sum().reset_index()
        goals_by_team_away = fixtures_data.groupby('away_team')['away_goals'].sum().reset_index().rename(columns={'away_team': 'home_team', 'away_goals': 'home_goals'})

        # Usando pd.concat() para combinar os DataFrames
        goals_by_team = pd.concat([goals_by_team_home, goals_by_team_away]).groupby('home_team')['home_goals'].sum().reset_index()

        fig_goals_total = px.bar(
            goals_by_team,
            x='home_team',
            y='home_goals',
            title='Gols Totais por Time',
            labels={'home_team': 'Time', 'home_goals': 'Total de Gols'},
            color='home_team',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_goals_total)

        # Média de Gols por Rodada

        # Garantindo que a coluna 'date' seja convertida para datetime
        fixtures_data['date'] = pd.to_datetime(fixtures_data['date'])
        # Agora você pode usar o acessador .dt
        fixtures_data['round'] = fixtures_data['date'].dt.strftime('%U')  # Agrupa por número da rodada
        average_goals_per_round = fixtures_data.groupby('round').agg({'home_goals': 'mean', 'away_goals': 'mean'}).reset_index()
        average_goals_per_round['average'] = (average_goals_per_round['home_goals'] + average_goals_per_round['away_goals']) / 2

        fig_avg_goals_round = px.line(
            average_goals_per_round,
            x='round',
            y='average',
            title='Média de Gols por Rodada',
            labels={'round': 'Rodada', 'average': 'Média de Gols'}
        )
        st.plotly_chart(fig_avg_goals_round)

        # Resultados de Casa versus Fora
        home_results = fixtures_data['home_goals'].value_counts().reset_index()
        away_results = fixtures_data['away_goals'].value_counts().reset_index()

        home_results.columns = ['Gols', 'Total']
        away_results.columns = ['Gols', 'Total']

        fig_home_away_results = go.Figure()
        fig_home_away_results.add_trace(go.Bar(x=home_results['Gols'], y=home_results['Total'], name='Casa', marker_color='blue'))
        fig_home_away_results.add_trace(go.Bar(x=away_results['Gols'], y=away_results['Total'], name='Fora', marker_color='orange'))

        fig_home_away_results.update_layout(title='Resultados de Casa versus Fora', xaxis_title='Gols', yaxis_title='Total', barmode='group')
        st.plotly_chart(fig_home_away_results)

    else:
        st.write("Nenhum dado encontrado para gerar gráficos.")
