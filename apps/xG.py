from numpy.core.numeric import True_
from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'
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

def app():
    st.write(
        """
        # Gráfica de Goles vs Goles esperados por jugador
        """
    )
    lista_ligas=list(ligas.keys())
    lista_ligas.insert(0,'Seleccionar')
    liga=st.selectbox('Seleccionar liga',lista_ligas,0)

    if liga!='Seleccionar':
        teams= extract_teams(ligas[liga])
        equipo = st.selectbox('Seleccionar equipo', ['Seleccionar']+list(teams['name']),0 )
        if equipo != 'Seleccionar':
            team_id=teams.loc[teams['name']==equipo,'id'].values[0]
            jugadores=show_players(team_id)
            jugadores=jugadores[['id','firstname','lastname','position1_name']]
            jugadores=jugadores[jugadores['position1_name']!='Goalkeeper']

            ordered_df=consolidar_jugadores(jugadores,liga)
            
            my_range=range(1,len(ordered_df.index)+1)

            fig=plt.figure(figsize=(10,12))
            plt.hlines(y=my_range, xmin=ordered_df['xG'], xmax=ordered_df['Goals'], color='white', alpha=0.4)
            plt.scatter(ordered_df['xG'], my_range, color='white', alpha=1, label='xG',s=100)
            plt.scatter(ordered_df['Goals'], my_range, color=color_xpecta, alpha=1 , label='Goles',s=100)
            plt.legend(loc=4)

            plt.yticks(my_range, ordered_df['Jugador'])
            plt.title("Goles vs xG", loc='left')
            plt.xlabel('Valor')
            plt.ylabel('Jugador')
            st.write("""
                ## Gráfica 1
            """)
            st.pyplot(fig)
            st.write("""
                ## Gráfica 2
            """)
            fig2=plt.figure(figsize=(8,10))
            ordered_df['player_name']=ordered_df['Jugador'].apply(borrar_apellido)
            
            plt.scatter(ordered_df['xG'], ordered_df['Goals'], color=color_xpecta)
            plt.plot( [0,ordered_df['Goals'].max()+1],[0,ordered_df['Goals'].max()+1] ,color='white',linestyle='dashed')
            goles=True
            for idx,row in ordered_df.iterrows():
                xG=row['xG']
                gol=row['Goals']
                nombre=row['player_name']
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

            disp_df=ordered_df.sort_values('Goals',ascending=False)[['Jugador','Goals','xG','xG per shot','Minutes played']].reset_index(drop=True).set_index('Jugador')
            st.dataframe(disp_df.style.format({'Goals':'{:.0f}','xG':'{:.2f}','xG per shot':'{:.2f}','Minutes played':'{:.0f}'}))