# BIBLIOTECAS 
import pandas as pd 
import re 
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
from folium.plugins import MarkerCluster
import numpy as np

from streamlit_folium import folium_static

#=====================================================================================
# Expandindo o layut da pagina do DASHBOARD:
#===================================================================================== 
st.set_page_config( page_title='Visão Empresa', layout='wide', page_icon='🍴')


#=====================================================================================
# FUNÇÕES
#===================================================================================== 
def clean_code( df ):
    """
       Esta função tem a responsabilidade de limpar o dataframe

       Tipos de limpeza: 
       1. Remoção dos dados NaN
       2. Mudança do tipo da coluna de dados
       3. Remoçãodos espaços das variáveis de texto
       4. Formatação da coluna de datas
       5. Limpeza das colunas de temp (Remoção do texto da variável numérica)
    
       input: Dataframe
       output: Fataframe
    """
    
    # 1. tirando os valores vazios (NaN) dascolunas selecionadas:
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :].copy()

    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :].copy()

    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :].copy() 
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :].copy()
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :].copy() 
    # 1. Convertendo a coluna Age de texto para numero 
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int ) 
    # 2. convertendo a coluna Ratings de texto para numero decimal (Float)  
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    # 3. convertendo acoluna order_date de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    # 4. convertendo multiples_deliverys de texto para numero (int)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    
    # 5. remover espaço da string de uma coluna de forma mais eficiente: 
    df.loc[:,'ID'] = (df.loc[:,'ID'].str.strip())    
    df.loc[:,'Delivery_person_ID'] = (df.loc[:,'Delivery_person_ID'].str.strip()) 
    df.loc[:,'Road_traffic_density'] = (df.loc[:,'Road_traffic_density'].str.strip())
    df.loc[:,'Type_of_vehicle'] = (df.loc[:,'Type_of_vehicle'].str.strip())    
    df.loc[:,'Type_of_order'] = (df.loc[:,'Type_of_order'].str.strip())
        # 7. Limpando a coluna de time taken (tempo de entrega) 
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split('(min)')[1])  
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)    
    return df 

    #grpafico barras
def order_metric( df ):
    # selecao de linhas:
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index() 
        
    #desenhar o gráfico de linhas
    fig = px.bar( df_aux, x='Order_Date', y='ID' )
    return fig
#gráfic pie
def distrib_pedid_tráfego( df ):
    # Código Gráfico_02:           
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
            
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )   
    st.plotly_chart(fig, use_container_width=True)
    return fig
#gráfic scatter
def delivery_city_traffic( df ):
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index() 
    #Plotando o grafico de bolha: 
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    st.plotly_chart(fig, use_container_width=True)
    return fig
def order_by_week( df ):
    #Criando coluna de semana, mostra o numero da semana que essa data está. 
    df['week_of_year'] = df['Order_Date'].dt.strftime ( '%U')
    #Criando a tabela com o agrupamento dos dados necessários.
    df_aux = df.loc[:, ['week_of_year', 'ID']].groupby('week_of_year').count().reset_index() 
    #Criando um gráfico de linhas com o plotly.express.
    fig = px.line(df_aux, x='week_of_year', y='ID')
     
    return fig

def order_share_by_week( df ):
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    st.plotly_chart(fig, use_container_width=True)
    return  fig 

# def country_maps( df ):
#     cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
#     df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
#     map_ = folium.Map() 
#     for index, location_info in df_aux.iterrows():
#         folium.Marker( [location_info['Delivery_location_latitude'], 
#                         location_info['Delivery_location_longitude']],
#                         popup=location_info[['City', 'Road_traffic_density']] ).add_to ( map_ )
    
#         folium_static( map_, width=1024, height=600 )
#         return None

 
def country_maps(df):
    map_ = folium.Map(location=[df['Delivery_location_latitude'].mean(), df['Delivery_location_latitude'].mean()], zoom_start=3, tiles='OpenStreetMap')

    marker_cluster = MarkerCluster().add_to(map_)

    for lat, lon, name, traffic in zip(df['Delivery_location_latitude'], df['Delivery_location_latitude'], df['City'], df['Road_traffic_density']):
        folium.Marker(
            location=[lat, lon],
            popup=f"{name}\n{traffic}",
            icon=folium.Icon(icon='pushpin')
        ).add_to(marker_cluster)
        
    return map_

#----------------------- INICIO DA ESTRUTURA LÓGICA ---------------------
#=====================================================================================
# IMPORTANDO DATASET
#===================================================================================== 
#df = pd.read_csv(r'C:\Users\Administrador\Documents\repos\03_FTC\FTC_PROJETOS\analise_com_streamlit\dataset\train.csv')
df = pd.read_csv('dataset/train.csv')
#=====================================================================================
# LIMPANDO DADOS
#=====================================================================================
df = clean_code (df) 

#=====================================================================================
#BARRA LATERAL esquerda) 53_module_empresa.py
#===================================================================================== 

#textos
st.header( 'Marketplace - Visão Cliente' ) 

#imagem
#image_path = 'C:\\Users\\Administrador\\Documents\\repos\\03_FTC\\FTC_PROJETOS\\analise_com_streamlit\\imagem_ds1.png'
image = Image.open( 'imagem1.png' )
st.sidebar.image( image, width=70 ) 



#textos
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' ) 
st.sidebar.markdown( """---""") 

### criando um slider e uma seleção
st.sidebar.markdown( '## Selecione uma data limite:' )

date_slider = st.sidebar.slider( 
    'Ate qual valor?',         
    value=pd.datetime( 2022, 4 ,13 ), 
    max_value=pd.datetime( 2022, 2 , 11 ), 
    min_value=pd.datetime( 2022, 4 , 6 ),  
    format='DD-MM-YYYY' )
min_value=pd.datetime( 2022, 4 , 6 )
#Exibindo o slider escolhido.
st.header( date_slider )

## criando seleção
st.sidebar.markdown("## Selecione as condições de transito que deseja:") 
traffic_options = st.sidebar.multiselect( 
    'Quais as condições do transito?',
    ['low', 'Medium', 'High', 'Jam'],
    default=['low', 'Medium', 'High', 'Jam'] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by William Moura')

#=====================================================================================
#FILTROS
#===================    ================================================================== 
#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :] 

#Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#=====================================================================================
######################     LAYOUT dos GRÁFICOS
#===================================================================================== 
 
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] ) 
 
with tab1:  
    with st.container(): 
        st.markdown("### 1° Gráfico  - Quantidade de entregas por datas.")

        fig = order_metric( df )
        st.plotly_chart(fig, use_container_width=True)
         
    with st.container(): 
        col1, col2 = st.columns( 2 ) 
        with col1: 
            st.markdown('### 2° Gráfico - Distribuição dos pedidos por tipo de tráfego.')
            fig = distrib_pedid_tráfego( df )
            st.plotly_chart(fig, use_container_width=True)
      
        with col2: 
            # title: 
            st.markdown('### 3° Gráfico -  Comparação do volume de pedidos por cidade e tipo de tráfego.') 

            fig = delivery_city_traffic( df )
            st.plotly_chart(fig, use_container_width=True)

            
with tab2: 
    with st.container():
        st.markdown("### 4° Gráfico ")

        fig = order_by_week( df )
        st.plotly_chart( fig, use_container_width=True )

        
    
    with st.container(): 
        st.markdown("### 5° Gráfico" ) 
         
        fig = order_share_by_week( df )
        st.plotly_chart(fig , use_container_width=True)

        
with tab3:
     with st.container():
        st.markdown('### 6° Gráfico')

        country_maps( df )
        
        
