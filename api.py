import streamlit as st
from modelo import *
import requests
from bs4 import BeautifulSoup
from io import StringIO
from urllib.request import urlopen

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

@st.cache
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
    
@st.cache
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

@st.cache
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
@st.cache
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
@st.cache
def players_match_match(player_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=xml'
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
@st.cache
def show_player_stats(player_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=61&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=csv'
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
@st.cache
def players_match_match(player_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=json'
    try:
        response = urlopen(url)
        data = json.loads(response.read())
    except:
        print(f'No se encontró {player_id}')
        return pd.DataFrame()
    output = pd.DataFrame()
    for i in data['data']['match']:
        dict_temp={'Partido': i['title'],'Id Jugador':i['team'][0]['player'][0]['id'],'Jugador':i['team'][0]['player'][0]['name']}
        for j in i['team'][0]['player'][0]['param']:
            dict_temp[j['name']]= j['value']
        output = output.append(dict_temp, ignore_index=True)
    output.fillna(0,inplace=True)
    return output

@st.cache(suppress_st_warning=True)
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

@st.cache(suppress_st_warning=True)
def team_match_match(team_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=43&team_id={team_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=json'
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


@st.cache(suppress_st_warning=True)
def partidos_liga(equipos,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    part=pd.DataFrame()
    for idx in equipos['id'].unique():
        print(idx)
        tmm=team_match_match(idx,tournament_id,season_id,fecha_inicio)
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

def plotear_xG(part,equipo):
    jornada_max=part.loc[part['Equipo']==equipo,'Jornada'].max()
    fig2=plt.figure(figsize=(10,2))
    per25=np.percentile(part.groupby('Equipo').mean()['xG'],25)
    per50=np.percentile(part.groupby('Equipo').mean()['xG'],50)
    per75=np.percentile(part.groupby('Equipo').mean()['xG'],75)

    plt.axvspan(per25, per50, color='orange', alpha=0.5)
    plt.axvspan(per50, per75, color='yellow', alpha=0.5)
    plt.axvspan(per75, 3.2, color='green', alpha=0.5)
    
    for idx,row in part.groupby('Equipo').mean().iterrows():
        eq=idx
        xg=row['xG']
        if eq==equipo:
            plt.scatter(row['xG'],1,color='white',s=200,zorder=11,label="Promedio Temporada")
        else:
            plt.scatter(row['xG'],1,color='grey',zorder=10)
    plt.title("xG")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'xG'].values[0],linestyle='--',color='white',zorder=10,label="Ultimo partido")
    plt.axvspan(0, per25, color='red', alpha=0.5)

    if part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'xG'].values[0] < part.groupby('Equipo').mean()['xG'].min():
        xop_min2= part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'xG'].values[0] - 0.05
    else:
        xop_min2=part.groupby('Equipo').mean()['xG'].min() - 0.05
    if part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'xG'].values[0] < part.groupby('Equipo').mean()['xG'].max():
        xop_max2=part.groupby('Equipo').mean()['xG'].max() + 0.05
    else:
        xop_max2= part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'xG'].values[0] + 0.05
    #plt.legend(loc=3)
    plt.xlim((xop_min2,xop_max2))
    st.pyplot(fig2)

def plotear_OpxG(part,equipo):
    jornada_max=part.loc[part['Equipo']==equipo,'Jornada'].max()
    fig=plt.figure(figsize=(10,2))
    per25=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],25)
    per50=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],50)
    per75=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],75)

    plt.axvspan(per25, per50, color='yellow', alpha=0.5)
    plt.axvspan(per50, per75, color='orange', alpha=0.5)
    plt.axvspan(per75, 3.2, color='red', alpha=0.5)

    for idx,row in part.groupby('Equipo').mean().iterrows():
        eq=idx
        xg=row['Opponent xG']
        if eq==equipo:
            plt.scatter(xg,1,color='white',s=200,zorder=11,label='Promedio Temporada')
        else:
            plt.scatter(xg,1,color='grey',zorder=10)
    plt.title("Opponent xG")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'Opponent xG'].values[0],linestyle='--',color='white',zorder=10,label='Ultimo partido')
    plt.axvspan(0, per25, color='green', alpha=0.5)
    if part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'Opponent xG'].values[0] < part.groupby('Equipo').mean()['Opponent xG'].min():
        xop_min= part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'Opponent xG'].values[0] - 0.05
    else:
        xop_min=part.groupby('Equipo').mean()['Opponent xG'].min() - 0.05
    if part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'Opponent xG'].values[0] < part.groupby('Equipo').mean()['Opponent xG'].max():
        xop_max= part.groupby('Equipo').mean()['Opponent xG'].max() + 0.05
    else:
        xop_max=part.loc[(part['Jornada']==jornada_max)&(part['Equipo']==equipo),'Opponent xG'].values[0] + 0.05
    plt.xlim((xop_min,xop_max))
    plt.gca().invert_xaxis()
    #plt.legend(loc=3)
    st.pyplot(fig)

@st.cache
def descargar_partidos(id_equipo,partidos):
    local = partidos['team1_id'] ==  id_equipo
    visitante = partidos['team2_id'] ==  id_equipo
    partidos_equipo = partidos[local | visitante ]
    eventos = pd.DataFrame()
    for i in partidos_equipo.id :
        temporal = show_match_events(str(i))
        eventos = pd.concat([eventos, temporal], ignore_index=True)
    eventos = eventos[eventos['player_id'].notna()]
    eventos['player_id'] = eventos['player_id'].astype(int)
    return eventos


@st.cache
def filtrar_eventos(eventos, id_team):
    filtrados = eventos[eventos['team_id']==id_team]
    return filtrados





def calculate_xG(df):
    x_tot=105
    y_der=24.85
    y_izq=43.15
    y_centro=34

    b=[ -1.2111 , 0.6653, -0.1039 ]

    df['numerador']=(x_tot-df['pos_x'])*(x_tot-df['pos_x'])+(y_izq-df['pos_y'])*(y_der-df['pos_y'])
    df['denominador']=np.sqrt((x_tot-df['pos_x'])**2 + (y_der-df['pos_y'])**2 ) * np.sqrt((x_tot-df['pos_x'])**2 + (y_izq-df['pos_y'])**2)
    df['angulo']=np.arccos(df['numerador']/df['denominador'])
    df['distancia']=np.sqrt((x_tot-df['pos_x'])**2+(y_centro-df['pos_y'])**2)
    df['Suma'] = -b[0]-b[1]*df['angulo']-b[2]*df['distancia']
    df['xG'] = 1/(1+np.exp(df['Suma']))

    return df

def tiros_jugador(data):

    col1, col2 = st.columns(2)
    tiros=['Shot on target', 'Shot into the bar/post', 'Shot blocked', 'Shot blocked by field player', 'Goal', 'Wide shot']
    tirosygoles = data[data['action_name'].isin(tiros)]
    tirosygoles = calculate_xG(tirosygoles)
    tiros = tirosygoles[tirosygoles['action_name']!='Goal']
    goles = tirosygoles[tirosygoles['action_name']=='Goal']
    #Create figure
    fig=plt.figure()
    fig.set_size_inches(5.25, 6.8)
    ax=fig.add_subplot(1,1,1)
    #Pitch Outline & Centre Line
    plt.plot([0,0],[0,68], color="grey")
    plt.plot([0,105],[68,68], color="grey")
    plt.plot([105,105],[68,0], color="grey")
    plt.plot([105,0],[0,0], color="grey")
    plt.plot([52.5,52.5],[0,68], color="grey")
    #Left Penalty Area
    plt.plot([16.5,16.5],[54.15,13.85],color="grey")
    plt.plot([0,16.5],[54.15,54.15],color="grey")
    plt.plot([16.5,0],[13.85,13.85],color="grey")
    #Right Penalty Area
    plt.plot([105,88.5],[54.15,54.15],color="grey")
    plt.plot([88.5,88.5],[54.15,13.85],color="grey")
    plt.plot([88.5,105],[13.85,13.85],color="grey")
    #Left 6-yard Box
    plt.plot([0,5.5],[43.15,43.15],color="grey")
    plt.plot([5.5,5.5],[24.85,43.15],color="grey")
    plt.plot([5.5,0],[24.85,24.85],color="grey")
    #Right 6-yard Box
    #plt.plot([99.5,105],[24.85,24.85],color="grey")​
    plt.plot([105,99.5],[43.15,43.15],color="grey")
    plt.plot([99.5, 99.5],[43.15,24.85],color="grey")
    plt.plot([99.5, 105], [24.85, 24.85], color = 'grey')
    #Prepare Circles
    centreCircle = plt.Circle((52.5,34),9.15,color="grey",fill=False)
    centreSpot = plt.Circle((52.5,34),0.8,color="grey")
    #Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)

    #Prepare Arcs
    rightArc = Arc((94,34),height=18.3,width=18.3,angle=0,theta1=127,theta2=234,color="grey")
    #Draw Arcs
    ax.add_patch(rightArc)
    plt.ylim(0, 68)
    plt.xlim(52.5, 105)
    #Tidy Axes
    plt.axis('off')
    for i in tiros.index:
        plt.plot(tiros['pos_x'][i],tiros['pos_y'][i],'o',  markeredgecolor = 'red',  markersize = 80*tiros['xG'][i], color='red', alpha=0.5)
    for i in goles.index:
        plt.plot(goles['pos_x'][i],goles['pos_y'][i],  'o', markeredgecolor = 'cyan', markersize = 80*goles['xG'][i],  color='cyan', alpha=0.5)

    plt.plot(1,1,'o', markersize =7, markeredgecolor = 'red', color='red', alpha=0.5, label = 'Tiros')
    plt.plot(1,1,'o', markersize =7, markeredgecolor = 'cyan', color='cyan', alpha=0.5, label = 'Goles')
    plt.plot(1,1,'o', markersize =7, markeredgecolor = 'black', color=  'black' ,label = '   ')

    plt.plot(1,1,'o', markersize =9, markeredgecolor = 'white', color=  'black' ,label = ' ')
    plt.plot(1,1,'o', markersize =11, markeredgecolor = 'white', color=  'black' ,label = 'xG')
    plt.plot(1,1,'o', markersize =13, markeredgecolor = 'white', color=  'black' ,label = '  ')
    #plt.plot(1,1,'o', markersize =15, markeredgecolor = 'white', color=  'black' ,label = '    ')


    plt.legend(loc = 'upper left', ncol=2)
    col1.pyplot(fig)
    #Create figure
    fig2=plt.figure()
    #fig.set_size_inches(16, 8)
    ax=fig2.add_subplot(1,1,1)

    plt.plot([-9,9],[0,0], color="grey")
    plt.plot([-5,-5],[0,3.5], color="grey")
    plt.plot([5,5],[0,3.5], color="grey")
    plt.plot([-5,5],[3.5,3.5], color="grey")

    plt.plot([-4.5,4.5],[3.7,3.7], color="grey")
    plt.plot([-5,-4.5],[3.5,3.7], color="grey")
    plt.plot([4.5,5],[3.7,3.5], color="grey")

    plt.plot([-4.5,-4.5],[1,3.7], color="grey")
    plt.plot([-5,-4.5],[0,1], color="grey")
    plt.plot([4.5,5],[1,0], color="grey")
    plt.plot([-4.5,4.5],[1,1], color="grey")
    plt.plot([4.5,4.5],[1,3.7], color="grey")

    plt.ylim(-1, 8)
    plt.xlim(-9, 9)
    plt.axis('off')
    for i in tiros.index:
        plt.plot(tiros['gate_x'][i],tiros['gate_y'][i],'o', markersize =  80*tiros['xG'][i], markeredgecolor = 'red', color='red', alpha=0.5)
    for i in goles.index:
        plt.plot(goles['gate_x'][i],goles['gate_y'][i],  'o', markersize =80*goles['xG'][i], markeredgecolor = 'cyan', color='cyan', alpha=0.5)

    plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'red', color='red', alpha=0.5, label = 'Tiros')
    plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'cyan', color='cyan', alpha=0.5, label = 'Goles')
    plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'black', color=  'black' ,label = '   ')

    p1 = ax.plot(1, -11, 'o', markersize = 7, markeredgecolor = 'white', color='black', label = ' ')
    p2 = ax.plot(1, -11, 'o', markersize = 9, markeredgecolor = 'white', color='black', label = 'xG')
    p3 = plt.plot(1, -11, 'o', markersize = 11, markeredgecolor = 'white', color='black', label = '  ')

    plt.legend(loc = 'upper left', ncol = 2)

    col2.pyplot(fig2)