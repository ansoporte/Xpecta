import streamlit as st
from modelo import *


def search_options(n, df_in):
    df_temp = copy.deepcopy(df_in)
    with st.beta_expander(f'Buscar jugador {n}'):
        list_seasons = sorted(list(df_temp['Season'].unique()), reverse=True)
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons, key=str(n))
        df_temp = df_temp[df_temp['Season'].isin([season])]
        league = st.selectbox('Liga', sorted(list(df_temp['League'].unique())), key=str(n+10))
        df_temp = df_temp[df_temp['League'].isin([league])]
        team = st.selectbox('Equipo', sorted(df_temp.index.get_level_values('Team').unique().tolist()), key=str(n+10000))
        df_temp = df_temp[df_temp.index.get_level_values('Team').isin([team])]
        list_names = sorted(df_temp.index.get_level_values('Name').unique().tolist())
        list_names.insert(0, '--Buscar--')
        pl_name = st.selectbox('Escriba o seleccione jugador', list_names, key=str(n+100))
        if '--Buscar--' not in pl_name:
            df_temp = df_temp[df_temp.index.get_level_values('Name').isin([pl_name])]
            return df_temp
        else:
            return pd.DataFrame()
def app():
    st.write("""
             # Comparar jugadores
             > Radar + tabla de estadísticas de jugadores seleccionados.
             """)
    bool_arqueros = st.checkbox('¿Va a comparar arqueros?')

    df_ju = base_jugadores()
    df_gk = base_arqueros()

    if bool_arqueros:
        posicion = 'Arquero'
        w = weights(posiciones[posicion])
        w.rename(index = {np.NaN:"xG conceded - Goals conceded"}, inplace = True)
        df = copy.deepcopy(df_gk)
        df["xG conceded - Goals conceded"]=df['xG conceded']-df['Goals conceded']
        df[w.index.tolist()]=df[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
    else:
        df = copy.deepcopy(df_ju)
    df = df[~df['League'].isin(['---'])]
    df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
    df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
    df_raw = copy.deepcopy(df)
    percentile(df)

    n_search = st.number_input('¿Cuantos jugadores va a comparar?', min_value=1, max_value=10)
    df_radar = pd.DataFrame()
    for n in range(0,n_search):
        df_selection = search_options(n+1, df)
        if len(df_selection)!=0:
            df_radar = df_radar.append(df_selection)

    if len(df_radar)!=0:
        st.write("""## Parámetros de gráficas""")
        N_variables = st.slider('Número de variables en radar', 5,12)
        if not bool_arqueros:
            lista_posiciones = sorted(list(posiciones.keys()))
            lista_posiciones.insert(0,'--Buscar--')
            lista_posiciones.remove('Lateral')
            posicion = st.selectbox('Escriba o seleccione la posición de juego', lista_posiciones)
            if '--Buscar--' not in posicion:
                w = weights(posiciones[posicion])
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
                radar_streamlit(df_radar, df_raw, posiciones[posicion], w, N_variables)