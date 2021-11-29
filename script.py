import requests
from bs4 import BeautifulSoup
from io import StringIO
from urllib.request import urlopen
import datetime 
import time 
from tqdm import tqdm
import pandas as pd
import numpy as np
import json 
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
ligas={
    'Colombia - Liga Bet Play':217,
    'Colombia - Torneo Bet Play':407,
    'Argentina - Torneo 2021':5334,
    'Mexico - Liga MX':108,
    'Estados Unidos - MLS':41,
    'Internacional - Copa Libertadores':184
}

season_2021=27
season_2022=29
info=['xG','xG conversion','xG per shot','Goals','Shots','Minutes played']


def show_match_events(match_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=36&start_ms=0&match_id={match_id}&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
    

def extract_matches(tournament_id,season_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=35&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()


def extract_teams(tournament_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=32&tournament_id={tournament_id}&season_id=27&date_start=&date_end=&lang_id=1&lang=&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

def show_players(team_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=5&team_id={team_id}&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

def players_match_match(player_id,tournament_id=217,season_id=27):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=xml'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

def show_player_stats(player_id,tournament_id=217,season_id=27):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=61&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

def players_match_match(player_id,tournament_id=217,season_id=27):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=json'
    try:
        response = urlopen(url)
        data = json.loads(response.read())
    except:
        print(f'No se encontró {player_id}')
        return None
    output = pd.DataFrame()
    for i in data['data']['match']:
        dict_temp={'Partido': i['title'],'Id Jugador':i['team'][0]['player'][0]['id'],'Jugador':i['team'][0]['player'][0]['name']}
        for j in i['team'][0]['player'][0]['param']:
            dict_temp[j['name']]= j['value']
        output = output.append(dict_temp, ignore_index=True)
    output.fillna(0,inplace=True)
    return output


def consolidar_jugadores(jugadores,liga):
    jugadores_consolidado=pd.DataFrame()
    for idx in jugadores['id']:
        try:
            temp=players_match_match(idx,ligas[liga])
            jugadores_consolidado=pd.concat([jugadores_consolidado,temp])
        except:
            jugadores_consolidado=jugadores_consolidado
    jugadores_consolidado[['Goals','xG','xG per shot','Minutes played','Shots','xG conversion']]=jugadores_consolidado[['Goals','xG','xG per shot','Minutes played','Shots','xG conversion']].astype(float)
    df=jugadores_consolidado.groupby('Jugador').sum()[info].reset_index()
    ordered_df = df.sort_values(by='Goals')
    return ordered_df


def team_match_match(team_id,tournament_id=217,season_id=27):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=43&team_id={team_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=json'
    try:
        response = urlopen(url)
        data = json.loads(response.read())
    except:
        return pd.DataFrame()
    output = pd.DataFrame()
    for i in data['data']['match']:
        dict_temp={'Partido': i['title'],'Id Partido':i['id'],'Equipo':i['team'][0]['name'],'Jornada':int(data['data']['match'].index(i)+1)}
        for j in i['team'][0]['param']:
            dict_temp[j['name']]= j['value']
        output = output.append(dict_temp, ignore_index=True)
    output.fillna(0,inplace=True)
    return output



def partidos_liga(equipos,tournament_id=217,season_id=27):
    part=pd.DataFrame()
    for idx in equipos['id'].unique():
        print(idx)
        tmm=team_match_match(idx,tournament_id,season_id)
        part=pd.concat([part,tmm])
    part['Opponent xG']=np.nan
    part.reset_index(drop=True,inplace=True)
    for idx,row in part.iterrows():
        id_partido=row['Id Partido']
        equipo=row['Equipo']
        part.loc[idx,'Opponent xG']=part.loc[(part['Id Partido']==id_partido)&(part['Equipo']!=equipo),'xG'].values[0]
        part[['xG','Opponent xG']]=part[['xG','Opponent xG']].astype(float)
        part['Porteria 0']=part['Goals conceded'].apply(lambda x: 1 if x==0 else 0)
    return part



def time_in_range(start, end, current):
    """Returns whether current is in the range [start, end]"""
    return start <= current <= end

start = datetime.time(1, 30, 0)
end = datetime.time(2, 30, 0)


while True:
    current = datetime.datetime.now().time()
    if time_in_range(start,end,current):
        print("Actualizando Eventos...")
        for liga_t in ligas.keys():
            print(liga_t)
            liga=ligas[liga_t]
            partidos=extract_matches(liga,27)
            partidos=partidos[partidos['available_events']==True]
            consolidado_partidos=pd.DataFrame()
            with tqdm(total=partidos.shape[0]) as pbar:
                for idx,row in partidos.iterrows():
                    match_id=row['id']
                    partido=show_match_events(match_id)
                    partido['match_id']=match_id
                    partido['match_date']=row['match_date']
                    partido['match_name']=row['match_name']
                    consolidado_partidos=pd.concat([consolidado_partidos,partido])
                    pbar.update(1)
            consolidado_partidos.to_csv(f'Partidos_{liga}.csv')
        print("Actualizando Partidos...")
        for liga_t in ligas.keys():
            print(liga_t)
            consolidado_partidos=pd.DataFrame()
            equipos= extract_teams(ligas[liga_t])
            with tqdm(total=equipos.shape[0]) as pbar:
                for idx in equipos['id'].unique():
                    tmm=team_match_match(idx,ligas[liga_t])
                    consolidado_partidos=pd.concat([consolidado_partidos,tmm])
                    consolidado_partidos['Opponent xG']=np.nan
                    consolidado_partidos.reset_index(drop=True,inplace=True)
                    pbar.update(1)
            for idx_,row in consolidado_partidos.iterrows():
                id_partido=row['Id Partido']
                equipo=row['Equipo']
                consolidado_partidos.loc[idx_,'Opponent xG']=consolidado_partidos.loc[(consolidado_partidos['Id Partido']==id_partido)&(consolidado_partidos['Equipo']!=equipo),'xG'].values[0]
                consolidado_partidos[['xG','Opponent xG']]=consolidado_partidos[['xG','Opponent xG']].astype(float)
                consolidado_partidos['Porteria 0']=consolidado_partidos['Goals conceded'].apply(lambda x: 1 if x==0 else 0)
            consolidado_partidos.to_csv(f'MatchMatch_{ligas[liga_t]}.csv')
    time.sleep(2700)




