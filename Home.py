
#Bibliotecas
import streamlit as st
from PIL import Image

#=====================================================================================
# Expandindo o layut da pagina do DASHBOARD:
# Importando imagem/ Barra lateral/ Texto Explicativo:
#
st.set_page_config(
    page_title="Home",
    layout='wide'
    ) 

#image_path = 'C:\\Users\\Administrador\\Documents\\repos\\03_FTC\\FTC_PROJETOS\\analise_com_streamlit\\imagem_ds1.png'
image = Image.open( 'imagem1.png' ) 
st.sidebar.image( image, width=120 )

#textos
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' ) 
st.sidebar.markdown( """---""") 

st.write( "# Curry Company Grouth Dashboard" ) 
st.markdown(
    """ 
    Grouth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Grouth Dashboard?

    - Visão Empresa: 
       - Visão Gerencial: Métricas gerais de comportamento.
       - Visão Tática: indicadores semanais de crescimento.
       - Visão Geográfica: insights de geolocalização.

    - Visão Entregadores:
       - Acompanhamento dos indicadores semanais de crescimento.
       
    - Visão Restaurante: 
       - Indicadores semanais de crescimento dos restaurantes:

    ### Aks for help 
    - Cientista de Dados: William Moura
""" )


