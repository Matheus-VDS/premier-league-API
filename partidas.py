import http.client
import json
import sqlite3
import datetime

# Configuração da API
API_KEY = "1bc636fa0dmshdc367e8c5421ae5p1e3f0bjsn481c3e6a3755"  # Substitua pela sua chave de API
conn_api = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

# Função para conectar ao banco de dados
def get_connection():
    return sqlite3.connect('football_fixtures.db')

# Função para criar tabelas
def create_tables():
    conn_db = get_connection()
    cursor = conn_db.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS league (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        logo TEXT,
        flag TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        name TEXT,
        logo TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY,
        league_id INTEGER,
        home_team_id INTEGER,
        away_team_id INTEGER,
        date TEXT,
        status TEXT,
        home_score INTEGER,
        away_score INTEGER,
        FOREIGN KEY (league_id) REFERENCES league(id),
        FOREIGN KEY (home_team_id) REFERENCES teams(id),
        FOREIGN KEY (away_team_id) REFERENCES teams(id)
    )''')

    conn_db.commit()
    conn_db.close()

# Função para obter e inserir dados da API
def fetch_and_insert_fixtures():
    conn_api.request("GET", "/v3/fixtures?league=39&season=2024", headers=headers)
    res = conn_api.getresponse()
    data = res.read()

    # Decodificando JSON
    json_data = json.loads(data.decode("utf-8"))

    # Verificando se a chave 'response' está presente
    if 'response' in json_data:
        fixtures_data = json_data["response"]
    else:
        print("A chave 'response' não foi encontrada na resposta da API.")
        return

    # Conexão com o banco de dados SQLite
    conn_db = get_connection()
    cursor = conn_db.cursor()

    # Inserindo dados nas tabelas
    if fixtures_data:
        # Adiciona informações da liga
        league_data = fixtures_data[1]['league']
        cursor.execute('''INSERT OR REPLACE INTO league (id, name, country, logo, flag) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (league_data['id'], league_data['name'], league_data['country'], league_data['logo'], league_data['flag']))

        # Adiciona informações dos times e as partidas
        for fixture in fixtures_data:
            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']
            
            # Adicionando times se não existirem
            cursor.execute('''INSERT OR REPLACE INTO teams (id, name, logo) 
                              VALUES (?, ?, ?)''', 
                           (home_team['id'], home_team['name'], home_team['logo']))
            
            cursor.execute('''INSERT OR REPLACE INTO teams (id, name, logo) 
                              VALUES (?, ?, ?)''', 
                           (away_team['id'], away_team['name'], away_team['logo']))
            
            # Ajustando a inserção de dados da partida
            fixture_id = fixture['fixture']['id']
            league_id = league_data['id']
            home_team_id = home_team['id']
            away_team_id = away_team['id']
            date = fixture['fixture']['date']
            status = fixture['fixture']['status']['short']
            home_score = fixture['goals']['home']
            away_score = fixture['goals']['away']
            
            cursor.execute('''INSERT OR REPLACE INTO fixtures (id, league_id, home_team_id, away_team_id, date, status, home_score, away_score) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (fixture_id, league_id, home_team_id, away_team_id, date, status, home_score, away_score))

    conn_db.commit()
    conn_db.close()
    print("Dados inseridos com sucesso no banco de dados SQLite!")

# Função para obter jogos passados
def get_past_fixtures():
    conn_db = get_connection()
    cursor = conn_db.cursor()
    
    query = '''
    SELECT f.id, l.name AS league_name, ht.name AS home_team, at.name AS away_team,
           f.date, f.home_score, f.away_score
    FROM fixtures f
    JOIN league l ON f.league_id = l.id
    JOIN teams ht ON f.home_team_id = ht.id
    JOIN teams at ON f.away_team_id = at.id
    WHERE f.date < ?
    '''
    past_fixtures = cursor.execute(query, (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchall()
    conn_db.close()
    return past_fixtures

# Função para obter jogos futuros
def get_future_fixtures():
    conn_db = get_connection()
    cursor = conn_db.cursor()
    
    query = '''
    SELECT f.id, l.name AS league_name, ht.name AS home_team, at.name AS away_team,
           f.date
    FROM fixtures f
    JOIN league l ON f.league_id = l.id
    JOIN teams ht ON f.home_team_id = ht.id
    JOIN teams at ON f.away_team_id = at.id
    WHERE f.date >= ?
    '''
    future_fixtures = cursor.execute(query, (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchall()
    conn_db.close()
    return future_fixtures

# Função para atualização automática dos jogos futuros
def update_future_fixtures():
    conn_api.request("GET", "/v3/fixtures?league=39&season=2020&from=" + datetime.datetime.now().strftime("%Y-%m-%d"), headers=headers)
    res = conn_api.getresponse()
    data = res.read()

    json_data = json.loads(data.decode("utf-8"))
    fixtures_data = json_data.get("response", [])

    conn_db = get_connection()
    cursor = conn_db.cursor()

    for fixture in fixtures_data:
        fixture_id = fixture['fixture']['id']
        home_score = fixture['goals']['home']
        away_score = fixture['goals']['away']
        status = fixture['fixture']['status']['short']
        
        cursor.execute('''UPDATE fixtures 
                          SET home_score = ?, away_score = ?, status = ?
                          WHERE id = ?''', 
                       (home_score, away_score, status, fixture_id))

    conn_db.commit()
    conn_db.close()
    print("Atualização de jogos futuros realizada com sucesso.")

# Execução inicial
create_tables()
fetch_and_insert_fixtures()
update_future_fixtures()
