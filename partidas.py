import http.client
import json
import sqlite3

# Conexão com a API
conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "1bc636fa0dmshdc367e8c5421ae5p1e3f0bjsn481c3e6a3755",  # Substitua pela sua chave de API
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

# Requisição para obter informações sobre partidas
conn.request("GET", "/v3/fixtures?league=39&season=2020&team=33", headers=headers)

res = conn.getresponse()
data = res.read()

# Decodificando JSON
json_data = json.loads(data.decode("utf-8"))

# Imprimindo a resposta completa para depuração
print(json.dumps(json_data, indent=4))

# Verificando se a chave 'response' está presente
if 'response' in json_data:
    fixtures_data = json_data["response"]
else:
    print("A chave 'response' não foi encontrada na resposta da API.")
    fixtures_data = []

# Conexão com o banco de dados SQLite
conn_db = sqlite3.connect('football_fixtures.db')
cursor = conn_db.cursor()

# Criando tabelas
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

# Inserindo dados nas tabelas se a resposta contiver dados
if fixtures_data:
    # Adiciona informações da liga
    league_data = fixtures_data[0]['league']
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
        status = fixture['fixture']['status']  # Certifique-se de que isso é um valor simples
        home_score = fixture['goals']['home']  # Certifique-se de que isso é um valor simples
        away_score = fixture['goals']['away']  # Certifique-se de que isso é um valor simples
        
        # Certifique-se de que status, home_score e away_score sejam do tipo correto
        if isinstance(status, dict):
            status = status.get('status')  # Ajuste conforme a estrutura do JSON

        cursor.execute('''INSERT OR REPLACE INTO fixtures (id, league_id, home_team_id, away_team_id, date, status, home_score, away_score) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (fixture_id, league_id, home_team_id, away_team_id, 
                        date, status, home_score, away_score))

# Commit e fechamento da conexão
conn_db.commit()
conn_db.close()
print("Dados inseridos com sucesso no banco de dados SQLite!")
