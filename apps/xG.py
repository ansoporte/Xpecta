from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'

Shots = ['Own goal','Shot on target','Shot into the bar/post','Shot blocked','Shot blocked by field player','Goal','Wide shot']
x_tot=105
y_der=24.85
y_izq=43.15
y_centro=34
b=[ -1.2111 , 0.6653, -0.1039 ]
model_variables = ['angulo','distancia']
def borrar_apellido(nombre):
    etiqueta=''
    nombres=str(nombre).split(' ')
    try:
        if len(nombres)==2:
            etiqueta= nombres[0][0]+'. '+ nombres[1]
        else:
            etiqueta = nombres[0][0] +'. '+ nombres[-2]
        return etiqueta
    except:
        v=1

def calculate_xG(shot):
    bsum = -b[0]
    for i,v in enumerate(model_variables):
        bsum = bsum - b[i+1]*shot[v]
    xG = 1/(1+np.exp(bsum))
    return xG


@st.cache
def cargar_partidos_liga(id_liga):
    partidos=pd.read_csv(f'Partidos_{id_liga}.csv')
    return partidos 

def app():
    st.write(
        """
        # Gráfica de Goles vs Goles esperados por jugador
        """
    )
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",['Seleccionar']+list(ligas.keys()))
    if liga != 'Seleccionar':
        teams= extract_teams(ligas[liga])
        equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
        partidos_liga=cargar_partidos_liga(ligas[liga])
        if equipo != 'Seleccionar':
            team_id=teams.loc[teams['name']==equipo,'id'].values[0]
            partidos_equipo=partidos_liga[partidos_liga['team_id']==team_id]
            partidos_equipo['xG']=0
            partidos_equipo['Goles']=0


            partidos_equipo['numerador']=partidos_equipo.apply(lambda x : (x_tot-x['pos_x'])*(x_tot- x['pos_x'])+(y_izq-x['pos_y'])*(y_der-x['pos_y']) if (x['action_name'] in Shots) else np.nan, axis=1)
            partidos_equipo['denominador']=partidos_equipo.apply(lambda x: np.sqrt((x_tot-x['pos_x'])**2 + (y_der-x['pos_y'])**2 ) * np.sqrt((x_tot-x['pos_x'])**2 + (y_izq-x['pos_y'])**2) if (x['action_name'] in Shots) else np.nan,axis=1)
            partidos_equipo['angulo']=partidos_equipo.apply(lambda x: np.arccos(x['numerador']/x['denominador']) if (x['action_name'] in Shots) else np.nan , axis=1)
            partidos_equipo['distancia']=partidos_equipo.apply(lambda x: np.sqrt((x_tot-x['pos_x'])**2+(y_centro-x['pos_y'])**2) if (x['action_name'] in Shots) else np.nan,axis=1)
            partidos_equipo['Goles']=partidos_equipo['action_name'].apply(lambda x: 1 if x=='Goal' else 0)
            partidos_equipo['xG'] = partidos_equipo.apply(lambda x: calculate_xG(x) if x['standart_name']!='Penalty' else .75, axis=1)
            
            jug = partidos_equipo.groupby('player_name').sum()
            jugadores=show_players(team_id)
            jugadores=jugadores[['id','firstname','lastname','position1_name']]
            jugadores=jugadores[jugadores['position1_name']!='Goalkeeper']

            #ordered_df=consolidar_jugadores(jugadores,liga)
            ordered_df=jug.sort_values('Goles')
            my_range=range(1,len(ordered_df.index)+1)

            fig=plt.figure(figsize=(10,12))
            plt.hlines(y=my_range, xmin=ordered_df['xG'], xmax=ordered_df['Goles'], color='white', alpha=0.4)
            plt.scatter(ordered_df['xG'], my_range, color='white', alpha=1, label='xG',s=100)
            plt.scatter(ordered_df['Goles'], my_range, color=color_xpecta, alpha=1 , label='Goles',s=100)
            plt.legend(loc=4)

            plt.yticks(my_range, ordered_df.index)
            plt.title("Goles vs xG", loc='left')
            plt.xlabel('Valor')
            plt.ylabel('Jugador')
            st.write("""
                ## Gráfica
            """)
            st.pyplot(fig)
            st.write("""
                ## Tabla con datos
            """)

            st.write("""
                ## Gráfica 2
            """)
            fig2=plt.figure(figsize=(8,10))
            copy=ordered_df.reset_index()
            ordered_df['player_name']=copy['player_name'].apply(borrar_apellido)
            
            plt.scatter(ordered_df['xG'], ordered_df['Goles'], color=color_xpecta)
            plt.plot( [0,ordered_df['Goles'].max()+1],[0,ordered_df['Goles'].max()+1] ,color='white',linestyle='dashed')
            goles=True
            for idx,row in ordered_df.iterrows():
                xG=row['xG']
                gol=row['Goles']
                nombre=borrar_apellido(idx)
                if gol >= 1:
                    if goles:
                        goles=False
                        plt.text(xG+0.1, gol+0.2,nombre,color='white', size=10, bbox=dict(boxstyle="round",  ec='grey', fc='grey',alpha=.5 ))
                    else:
                        goles=True
                        plt.text(xG-0.1, gol-0.2,nombre,color='white', size=10, bbox=dict(boxstyle="round",  ec='grey', fc='grey',alpha=.5 ))

            plt.title("Goles vs xG", loc='left')
            plt.xlabel('Goles esperados generados')
            plt.ylabel('Goles marcados')
            st.pyplot(fig2)
            st.write("""
                ## Tabla con datos
            """)

            disp_df=ordered_df.sort_values('Goles',ascending=False)[['Goles','xG']]
            st.dataframe(disp_df.style.format({'Goals':'{:.0f}','xG':'{:.2f}'}))
