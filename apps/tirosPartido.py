import streamlit as st
from modelo import *
import requests
from bs4 import BeautifulSoup
from io import StringIO
from matplotlib.patches import Arc

"""
Ideas a agregar:
- Filtrar por equipo
- Filtrar por fecha
- Agregar botón de descarga a mano derecha
- Agregar botón de descargar todos como zip a lo ultimo de la página
"""

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

b=[ -1.2111 , 0.6653, -0.1039 ]
model_variables = ['angulo','distancia']
Shots = ['Own goal','Shot on tarhet','Shot into the bar/post','Shot blocked','Shot blocked by field player','Goal','Wide shot']
acciones =['Own goal','Shot on target', 'Shot into the bar/post', 'Shot blocked', 'Shot blocked by field player',  'Wide shot']
x_tot=105
y_der=24.85
y_izq=43.15
y_centro=34
def calculate_xG(shot):
    bsum = -b[0]
    for i,v in enumerate(model_variables):
        bsum = bsum - b[i+1]*shot[v]
    xG = 1/(1+np.exp(bsum))
    return xG
def mapa_tiros(eventos,equipoa,equipob,m1,m2,f):
    primerT=eventos[eventos['action_name']=='Half time']['second'].values[0]
    segundoT=eventos[eventos['action_name']=='Match end']['second'].values[0]
    duracion_partido=round((primerT+segundoT)/60)

    def calcular_minuto(row):
        if row['half']==1:
            minuto = round(row['second']/60)
        else:
            minuto = round((primerT+row['second'])/60)
        return minuto 

    shots = eventos[ eventos['action_name'].isin(Shots)].copy()
    shots['numerador']=(x_tot-shots['pos_x'])*(x_tot-shots['pos_x'])+(y_izq-shots['pos_y'])*(y_der-shots['pos_y'])
    shots['denominador']=np.sqrt((x_tot-shots['pos_x'])**2 + (y_der-shots['pos_y'])**2 ) * np.sqrt((x_tot-shots['pos_x'])**2 + (y_izq-shots['pos_y'])**2)
    shots['angulo']=np.arccos(shots['numerador']/shots['denominador'])
    shots['distancia']=np.sqrt((x_tot-shots['pos_x'])**2+(y_centro-shots['pos_y'])**2)
    shots['resultado']=shots['action_name'].apply(lambda x: 1 if x=='Goal' else 0)
    shots['xG'] = shots.apply(calculate_xG, axis=1)
    shots['minuto'] = shots.apply(calcular_minuto, axis=1)
    shots.loc[(shots['standart_name']=='Penalty'),'xG']=.75
    eventosa = shots[shots['team_name']==equipoa]
    tirosa=eventosa[eventosa['action_name'].isin(acciones)]
    golesa=eventosa[eventosa['action_name']=='Goal']

    eventosb = shots[shots['team_name']==equipob]
    tirosb=eventosb[eventosb['action_name'].isin(acciones)]
    golesb=eventosb[eventosb['action_name']=='Goal']
    
    y_equipo1 = []
    y_equipo2 = []
    construir_xG(shots,equipoa, y_equipo1,duracion_partido)
    construir_xG(shots,equipob, y_equipo2,duracion_partido)

    #Create figure
    fig=plt.figure()
    fig.set_size_inches(10.5, 6.8)
    ax=fig.add_subplot(1,1,1)
    #Pitch Outline & Centre Line
    plt.plot([0,0],[0,68], color="white")
    plt.plot([0,105],[68,68], color="white")
    plt.plot([105,105],[68,0], color="white")
    plt.plot([105,0],[0,0], color="white")
    plt.plot([52.5,52.5],[0,68], color="white")

    #Left Penalty Area
    plt.plot([16.5,16.5],[54.15,13.85],color="white")
    plt.plot([0,16.5],[54.15,54.15],color="white")
    plt.plot([16.5,0],[13.85,13.85],color="white")

    #Right Penalty Area
    plt.plot([105,88.5],[54.15,54.15],color="white")
    plt.plot([88.5,88.5],[54.15,13.85],color="white")
    plt.plot([88.5,105],[13.85,13.85],color="white")

    #Left 6-yard Box
    plt.plot([0,5.5],[43.15,43.15],color="white")
    plt.plot([5.5,5.5],[24.85,43.15],color="white")
    plt.plot([5.5,0],[24.85,24.85],color="white")

    #Right 6-yard Box
    plt.plot([105,99.5],[43.15,43.15],color="white")
    plt.plot([99.5, 99.5],[43.15,24.85],color="white")
    plt.plot([99.5,105],[24.85,24.85],color="white")

    #Prepare Circles
    centreCircle = plt.Circle((52.5,34),9.15,color="white",fill=False)
    centreSpot = plt.Circle((52.5,34),0.8,color="white")
    leftPenSpot = plt.Circle((11,34),0.8,color="white")
    rightPenSpot = plt.Circle((94,34),0.8,color="white")

    #Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)

    #Prepare Arcs
    leftArc = Arc((11,34),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="white")
    rightArc = Arc((94,34),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="white")
    #Draw Arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)
    
    plt.ylim(-5, 68)
    plt.xlim(0, 105)
    #Tidy Axes
    plt.axis('off')

    eventossa=shots[shots['team_name']==equipoa]
    tirosa=eventossa[eventossa['action_name'].isin(acciones)]
    golesa=eventossa[eventossa['action_name']=='Goal']

    eventossb=shots[shots['team_name']==equipob]
    tirosb=eventossb[eventossb['action_name'].isin(acciones)]
    golesb=eventossb[eventossb['action_name']=='Goal']

    for i in tirosa.index:
        plt.plot(105-tirosa['pos_x'][i],68-tirosa['pos_y'][i],'o', markersize = 80*tirosa['xG'][i], markeredgecolor = 'red', color='red', alpha=0.5)
    for i in golesa.index:
        plt.plot(105-golesa['pos_x'][i],68-golesa['pos_y'][i],  'o', markersize = 80 * golesa['xG'][i], markeredgecolor = 'blue', color='blue', alpha=0.5)

    for i in tirosb.index:
        plt.plot(tirosb['pos_x'][i],tirosb['pos_y'][i],'o', markersize = 80*tirosb['xG'][i], markeredgecolor = 'red', color='red', alpha=0.5)
    for i in golesb.index:
        plt.plot(golesb['pos_x'][i],golesb['pos_y'][i],  'o', markersize = 80 * golesb['xG'][i], markeredgecolor = 'blue', color='blue', alpha=0.5)

    plt.plot(-1,-1,  'o', markersize = 7.5, markeredgecolor = 'red', color='red', alpha=0.5, label='Tiros')
    plt.plot(-1,-1,   'o', markersize = 5.5, markeredgecolor = 'blue', color='blue', alpha=0.5, label='Goles')

    
    plt.text(6,63.7, 'xG: '+str(round(y_equipo1[-1],2)), color='white',weight='bold',fontsize=15)
    plt.text(87,63.7, 'xG: '+str(round(y_equipo2[-1],2)), color='white',weight='bold',fontsize=15)
    plt.legend(loc=(.45,.1))
    st.pyplot(fig)

def construir_xG(shots,equipo, y,duracion_partido):
    i=0
    xGs = [0] + list(shots[shots['team_name']==equipo]['xG'].cumsum(axis=0))
    mins = list(shots[shots['team_name']== equipo]['minuto']) + [duracion_partido]

    for min,xG in zip(mins, xGs):

        while i != min:
            y.append(xG)
            i+=1
    return y

def app():

    st.write(
        """
        # Mapa de tiros
        > Mapa de tiros por partido con goles esperados 
        """
    )
    liga = st.selectbox("Seleccione la Liga de la cual quiere ver los partidos",list(ligas.keys()))
    df=extract_matches(ligas[liga],season_2021)
    df=df[df['available_events']==True]
    lista_partidos = df['match_date'].str.replace('-','/').str.split(' ').str[0]+' - '+df['match_name']
    partidos = st.multiselect('Escriba o seleccione el(los) partido(s) a gráficar', lista_partidos)
    
    if partidos:
        partido_split = [partido.split(' - ',1)[1] for partido in partidos]
        ids=list(df.loc[df['match_name'].isin(partido_split),'id'])
        
        st.write(
            """
            #
            """
        )
        st.write(
            """
            # Mapas
            """
        )

        for id_ in ids:
            equipo1=df.loc[df.id==id_,'team1_name'].values[0]
            marcador1=df.loc[df.id==id_,'team1_score'].values[0]
            marcador2=df.loc[df.id==id_,'team2_score'].values[0]
            equipo2=df.loc[df.id==id_,'team2_name'].values[0]
            eventos =show_match_events(id_)
            fecha=df.loc[df.id==id_,'match_date'].values[0].split(' ')[0]
            st.write(
                f"""
                ### **{equipo1} {marcador1} - {marcador2} {equipo2}**
                {fecha}
                """
                )
            mapa_tiros(eventos,equipo1,equipo2,marcador1,marcador2,fecha)
