from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'

def app():
    st.write(
        """
        # Estadísticas
        """
    )
    lista_ligas=list(ligas.keys())
    lista_ligas.insert(0,'Seleccionar')
    liga=st.selectbox('Seleccionar liga',lista_ligas,0)

    if liga!='Seleccionar':
        teams= extract_teams(ligas[liga])
        equipo = st.selectbox('Seleccionar equipo', ['Seleccionar']+list(teams['name']),0 )
        if equipo != 'Seleccionar':
            part = pd.read_csv(f'MatchMatch_{ligas[liga]}.csv')
            plotear_xG(part,equipo)
            plotear_OpxG(part,equipo)

            st.write("""
                # Top variables de equipo
            """)
            ranking=part.groupby('Equipo').sum()[['xG','Opponent xG','Porteria 0']]
            ranking['Top porteria 0']=ranking['Porteria 0'].rank(method='max',ascending=False).astype(int)
            ranking['Top xG']=ranking['xG'].rank(method='max',ascending=False).astype(int)
            ranking['Top xG Oponente']=ranking['Opponent xG'].rank(method='max').astype(int)

            st.write(ranking.loc[equipo,['Top porteria 0','Top xG','Top xG Oponente']])
            

            


    
        