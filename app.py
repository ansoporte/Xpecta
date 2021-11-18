import streamlit as st
from multiapp import MultiApp
from apps import home, ranking, pasesT,xG,barras,Tiros,rankingref,compjugadores, parecidos,onceideal, histjug


app=MultiApp()
app.add_app("INICIO",home.app)
app.add_app("RANKING",ranking.app)
app.add_app("RANKING POR REFERENTE", rankingref.app)
app.add_app("COMPARAR JUGADORES", compjugadores.app)
app.add_app("BUSCAR PARECIDOS",parecidos.app)
app.add_app("11 IDEAL",onceideal.app)
app.add_app("HISTÓRICO JUGADORES",histjug.app)
app.add_app("DIFERENCIA XG",xG.app)
app.add_app("ESTADÍSTICAS",barras.app)
app.add_app("MAPA DE TIROS",Tiros.app)
app.add_app("REDES DE PASES",pasesT.app)
#app.add_app("TIROS POR PARTIDO",tirosPartido.app)
#app.add_app("PRUEBA",prueba.app)
app.run()