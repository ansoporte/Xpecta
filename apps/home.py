import time
from PIL import Image
import streamlit as st
import os

def app():
    modificationTime = time.strftime('%d / %m / %Y', time.localtime(os.path.getmtime('Data/Jugadores2510.csv')))
    st.write("""
    #
    #
    #
    """)
    image = Image.open('Imagenes/nacional.png')
    col1, col2 = st.columns([1, 1])
    col1.image(image)
    col2.write("""
    #
    #
    ##
    # **X scout**
    > Scouting Engine -- ALPHA version --\n
    > Updated {}
    """.format(modificationTime))