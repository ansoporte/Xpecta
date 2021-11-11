import streamlit as st
from multiapp import MultiApp
from apps import home, ranking, rankingref,compjugadores, parecidos,onceideal, histjug


app=MultiApp()
app.add_app("INICIO",home.app)
app.add_app("RANKING",ranking.app)
app.add_app("RANKING POR REFERENTE", rankingref.app)
app.add_app("COMPARAR JUGADORES", compjugadores.app)
app.add_app("BUSCAR PARECIDOS",parecidos.app)
app.add_app("11 IDEAL",onceideal.app)
app.add_app("HISTÓRICO JUGADORES",histjug.app)
#app.add_app("TIROS POR PARTIDO",tirosPartido.app)
#app.add_app("PRUEBA",prueba.app)
app.run()