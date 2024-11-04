# Dashboard das partidas do Premier League 2024/2025

Este projeto é um dashboard interativo para visualizar estatísticas de partidas da Premier League usando Streamlit. A aplicação permite que os usuários visualizem diferentes gráficos relacionados a partidas, resultados e desempenho dos times.

## Requisitos

Antes de começar, verifique se você tem os seguintes itens instalados:

- [Python 3.7 ou superior](https://www.python.org/downloads/)

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/Matheus-VDS/premier-league-API.git
    cd premier-league-API

2. Crie e ative um ambiente virtual:

    python -m venv venv
    ## No Windows:
    venv\Scripts\activate
    ## No macOS/Linux:
    source venv/bin/activate

3. Instale as dependências necessárias:
    
    pip install -r requirements.txt

4. Execute o arquivo partidas.py para criar o banco de dados

    python partidas.py

5. Execute o Streamlit

    streamlit run app.py

## Tecnologias utilizadas

- Python
- SQLite3
- API-Football (https://www.api-football.com/)
- Streamlit
