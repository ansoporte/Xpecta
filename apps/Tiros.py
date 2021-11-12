from modelo import *
from api import *
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

def app():
    st.write('# Mapa de Tiros por Equipo')
    plt.style.use('dark_background')

    lista_ligas=list(ligas.keys())
    lista_ligas.insert(0,'Seleccionar')
    liga=st.selectbox('Seleccionar liga',lista_ligas,0)

    if liga!='Seleccionar':
        equipos = extract_teams(ligas[liga])
        escoger_partidos = st.checkbox('Escoger partidos')

        partidos=extract_matches(ligas[liga],season_2021)
        partidos=partidos[partidos['available_events']==True]
        
        equipo = st.selectbox('Seleccionar equipo', ['Seleccionar']+list(equipos['name']),0 )

        if equipo != 'Seleccionar':
            id_equipo = equipos.set_index('name').loc[equipo]['id']

            if escoger_partidos:
                local = partidos['team1_id'] ==  id_equipo
                visitante = partidos['team2_id'] ==  id_equipo
                partidos_equipo = partidos[local | visitante ]
                lista_partidos=partidos_equipo['match_date'].str.replace('-','/').str.split(' ').str[0]+' - '+partidos_equipo['match_name']
                partidos_escogidos = st.multiselect('Seleccionar partidos',list(lista_partidos) )
                eventos = pd.DataFrame()
                for partido in partidos_escogidos:
                    partido_split = partido.split(' - ',1)[1] 
                    id_partido = partidos.loc[partidos['match_name']==partido_split,'id'].values[0]
                    temporal = show_match_events(id_partido)
                    eventos = pd.concat([eventos,temporal],ignore_index=True)

            else:

                with st.spinner('Descargando eventos ...'):
                    eventos = descargar_partidos(id_equipo,partidos)

            eventos_filtrados = filtrar_eventos(eventos,id_equipo)
            tiros_jugador(eventos_filtrados)