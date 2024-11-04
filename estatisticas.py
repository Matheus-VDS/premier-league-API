import http.client
import json
import sqlite3

# Conexão com a API
conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "1bc636fa0dmshdc367e8c5421ae5p1e3f0bjsn481c3e6a3755",
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

conn.request("GET", "/v3/teams/statistics?league=39&season=2024&teams=61", headers=headers)
res = conn.getresponse()
data = res.read()

# Decodificando JSON
json_data = json.loads(data.decode("utf-8"))["response"]

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('football_statistics.db')
cursor = conn.cursor()

# Criando tabelas
cursor.execute('''CREATE TABLE IF NOT EXISTS league (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    logo TEXT,
    flag TEXT,
    season INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY,
    name TEXT,
    logo TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS fixtures (
    id INTEGER PRIMARY KEY,
    played_home INTEGER,
    played_away INTEGER,
    played_total INTEGER,
    wins_home INTEGER,
    wins_away INTEGER,
    wins_total INTEGER,
    draws_home INTEGER,
    draws_away INTEGER,
    draws_total INTEGER,
    loses_home INTEGER,
    loses_away INTEGER,
    loses_total INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    total_home INTEGER,
    total_away INTEGER,
    total INTEGER,
    average_home REAL,
    average_away REAL,
    average_total REAL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS goals_minute (
    minute_range TEXT PRIMARY KEY,
    total INTEGER,
    percentage TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS biggest (
    id INTEGER PRIMARY KEY,
    streak_wins INTEGER,
    streak_draws INTEGER,
    streak_loses INTEGER,
    wins_home TEXT,
    wins_away TEXT,
    loses_home TEXT,
    loses_away TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS clean_sheet (
    home INTEGER,
    away INTEGER,
    total INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS failed_to_score (
    home INTEGER,
    away INTEGER,
    total INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS penalty (
    scored_total INTEGER,
    scored_percentage TEXT,
    missed_total INTEGER,
    missed_percentage TEXT,
    total INTEGER
)''')

# Inserindo dados nas tabelas
league = json_data['league']
cursor.execute('''INSERT OR REPLACE INTO league (id, name, country, logo, flag, season) 
                  VALUES (?, ?, ?, ?, ?, ?)''', 
               (league['id'], league['name'], league['country'], league['logo'], league['flag'], league['season']))

team = json_data['team']
cursor.execute('''INSERT OR REPLACE INTO team (id, name, logo) VALUES (?, ?, ?)''', 
               (team['id'], team['name'], team['logo']))

fixtures = json_data['fixtures']
cursor.execute('''INSERT OR REPLACE INTO fixtures (id, played_home, played_away, played_total, wins_home, wins_away, wins_total,
                   draws_home, draws_away, draws_total, loses_home, loses_away, loses_total) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
               (1, fixtures['played']['home'], fixtures['played']['away'], fixtures['played']['total'],
                fixtures['wins']['home'], fixtures['wins']['away'], fixtures['wins']['total'],
                fixtures['draws']['home'], fixtures['draws']['away'], fixtures['draws']['total'],
                fixtures['loses']['home'], fixtures['loses']['away'], fixtures['loses']['total']))

goals = json_data['goals']['for']
cursor.execute('''INSERT OR REPLACE INTO goals (id, total_home, total_away, total, average_home, average_away, average_total) 
                  VALUES (?, ?, ?, ?, ?, ?, ?)''', 
               (1, goals['total']['home'], goals['total']['away'], goals['total']['total'], 
                goals['average']['home'], goals['average']['away'], goals['average']['total']))

for minute, details in goals['minute'].items():
    if details['total'] is not None:
        cursor.execute('''INSERT OR REPLACE INTO goals_minute (minute_range, total, percentage) 
                          VALUES (?, ?, ?)''', 
                       (minute, details['total'], details['percentage']))

biggest = json_data['biggest']
cursor.execute('''INSERT OR REPLACE INTO biggest (id, streak_wins, streak_draws, streak_loses, wins_home, wins_away, loses_home, loses_away) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
               (1, biggest['streak']['wins'], biggest['streak']['draws'], biggest['streak']['loses'],
                biggest['wins']['home'], biggest['wins']['away'], biggest['loses']['home'], biggest['loses']['away']))

clean_sheet = json_data['clean_sheet']
cursor.execute('''INSERT OR REPLACE INTO clean_sheet (home, away, total) 
                  VALUES (?, ?, ?)''', 
               (clean_sheet['home'], clean_sheet['away'], clean_sheet['total']))

failed_to_score = json_data['failed_to_score']
cursor.execute('''INSERT OR REPLACE INTO failed_to_score (home, away, total) 
                  VALUES (?, ?, ?)''', 
               (failed_to_score['home'], failed_to_score['away'], failed_to_score['total']))

penalty = json_data['penalty']
cursor.execute('''INSERT OR REPLACE INTO penalty (scored_total, scored_percentage, missed_total, missed_percentage, total) 
                  VALUES (?, ?, ?, ?, ?)''', 
               (penalty['scored']['total'], penalty['scored']['percentage'], penalty['missed']['total'], penalty['missed']['percentage'], penalty['total']))

# Commit e fechamento da conexão
conn.commit()
conn.close()
print("Dados inseridos com sucesso no banco de dados SQLite!")
