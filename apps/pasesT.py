from modelo import *
import pandas as pd
from api import *

@st.cache
def cargar_partidos_liga(id_liga):
    partidos=pd.read_csv(f'Partidos_{id_liga}.csv')
    return partidos 

def app():
    st.write(
        """
        # Mapa de pases totales
        """
    )
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",['Seleccionar']+list(ligas.keys()))
    if liga != "Seleccionar":
        teams= extract_teams(ligas[liga])
        equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
        if ligas[liga]==108:
            df = extract_matches(ligas[liga],season_2022)
        else:
            df = extract_matches(ligas[liga],season_2021)
        df = df[df['available_events']==True]
        partidos_liga=cargar_partidos_liga(ligas[liga])
        if equipo != 'Seleccionar':
            team_id=teams.loc[teams['name']==equipo,'id'].values[0]
            partidos_id = df.loc[(df['team1_id']==team_id)|(df['team2_id']==team_id),'id'].values.tolist()
            partidos = partidos_liga[partidos_liga['match_id'].isin(partidos_id)]
            matriz_de_pases(partidos,equipo)