-- Contar o número de vitórias em casa e fora para um time específico (ex: &quot;Liverpool&quot;)

SELECT

    SUM(CASE WHEN home_team_id = '34' AND home_score &gt; away_score THEN 1 ELSE 0 END) AS vitorias_casa,

    SUM(CASE WHEN away_team_id = '34' AND away_score &gt; home_score THEN 1 ELSE 0 END) AS vitorias_fora

FROM fixtures;