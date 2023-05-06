
#=====================================================================================
# BIBLIOTECAS 
#=====================================================================================
 
import pandas as pd 
import re 
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from haversine import haversine
 
import numpy as np
import plotly.graph_objects as go

#=====================================================================================
# Expandindo o layut da pagina do DASHBOARD:
#===================================================================================== 
st.set_page_config( page_title='Visão Empresa', layout='wide')   


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
    linhas_vazias = df['Time_taken(min)'] != 'NaN '
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

#A distancia média de todas as entregas
def delivery_distance( df, fig ):
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']
        #Achando a distancia do ponto de partida até o ponto de entrega
        df['distance'] = df.loc[:, cols].apply( lambda x: haversine( 
                                                        (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
                # o ('np.round' define a quantidade de casas decimais)                                        
        avg = np.round(df['distance'].mean(), 2)
        col2.metric( "A distancia média de todas as entregas é:", avg )
        return avg 

    else: 
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']

        #Achando a distancia do ponto de partida até o ponto de entrega
        df['distance'] = df.loc[:, cols].apply( lambda x: haversine( 
                                        (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )  

        
        avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()                               
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'],  values=avg_distance['distance'], pull=[ 0, 0.1, 0 ] )] )

        return fig 
                           


def festival_analytics( df, festival, op ): 
    """ 
    Esta função calcula a média e o desvio padrão do tempo de de entrega.

    Parâmetros:
        input:
        - there_festival: Colocar a variavel que seleciona se hou ou não festivalque no caso são ('Yes ' e 'No ').

        - estatistic:Colocar qual parâmetro estatítico você quer de retorno (mean_time, std_time).

        output: 
        - DataFrame com 2 colunas e 1 linha
    """
        
    df_aux1 = (  df.loc[:, [ 'Time_taken(min)', 'Festival']] 
                        .groupby('Festival') 
                        .agg({'Time_taken(min)': ['mean', 'std']})  )

    df_aux1.columns = ['mean_time', 'std_time']
    df_aux1 = df_aux1.reset_index()
            # o ('np.round' define a quantidade de casas decimais)
            # selecionando a linha e a coluna que vou expor:
    df_aux1 = np.round(df_aux1.loc[df_aux1['Festival'] == festival, op],  2)
    return df_aux1
            
def avg_std_time_graph( df ):
                
    df_aux = df.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['média', 'desviopadrão']
    df_aux = df_aux.reset_index()

    #plotando o gráfico de colunas:
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['média'], error_y=dict( type='data', array=df_aux['desviopadrão'])) )

    return fig


#####GRÁFICO DE bigPIZZA- TEMPO MEDIO E DESVIO PADRAO  PARA CADA CIDADE E TRÁFEGO
def avg_mean_std_by_city_traffic( df ): 

    df_aux1 =(  df.loc[:, [ 'Time_taken(min)', 'City', 'Road_traffic_density' ]] 
                        .groupby([ 'City', 'Road_traffic_density' ])
                        .agg({'Time_taken(min)': ['mean', 'std']})  )

    df_aux1.columns = ['avg_time', 'std_time']
    df_aux1 = df_aux1.reset_index()
    #Plotando o Gráfico:
    fig = px.sunburst(df_aux1, path=['City', 'Road_traffic_density'], values='avg_time',
                    color='std_time', color_continuous_scale='RdBu', 
                    color_continuous_midpoint=np.average(df_aux1['std_time']))
    return fig
#=====================================================================================
# IMPORTANDO DATAFRAME
#=====================================================================================   
#df = pd.read_csv(r'C:\Users\Administrador\Documents\repos\03_FTC\FTC_PROJETOS\analise_com_streamlit\dataset\train.csv')
df = pd.read_csv('dataset\train.csv')
#=====================================================================================
# LIMPEZA DOS DADOS 
#=====================================================================================
df = clean_code( df )

#=====================================================================================
#BARRA LATERAL (ESQUERDA)
#===================================================================================== 

#textos
st.title( 'Marketplace - Visão Restaurantes' ) 

#imagem
#image_path = 'C:\\Users\\Administrador\\Documents\\repos\\03_FTC\\FTC_PROJETOS\\analise_com_streamlit\\imagem_ds1.png'
image = Image.open( 'imagem1.png' )
st.sidebar.image( image, width=120 ) 



#textos
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' ) 
st.sidebar.markdown( """---""") 

#=====================================================================================
# CRIANDO UM SLIDER E UMA SELEÇÃO DOS DADOS (INPUT)
#===================================================================================== 

st.sidebar.markdown( '## Selecione uma data limite:' )

date_slider = st.sidebar.slider( 
    'Ate qual valor?',         
    value=pd.datetime( 2022, 4 ,13 ), 
    max_value=pd.datetime( 2022, 2 , 11 ), 
    min_value=pd.datetime( 2022, 4 , 6 ),  
    format='DD-MM-YYYY' )
min_value=pd.datetime( 2022, 4 , 6 )
#Exibindo o slider escolhido. 

##---------------------------------
st.sidebar.markdown("## Selecione as condições de transito que deseja:") 
traffic_options = st.sidebar.multiselect( 
    'Quais as condições do transito?',
    ['low', 'Medium', 'High', 'Jam'],
    default=['low', 'Medium', 'High', 'Jam'] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by William Moura')

#=====================================================================================
# FILTROS
#===================================================================================== 
#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :] 

#Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#=====================================================================================
#LAYOUT 
#=====================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-']) 
 
with tab1: 
    with st.container():
        st.markdown('All Metrics')
        st.markdown("""---""")
        
        col1, col2, col3= st.columns( 3, gap='large') 

        with col1: 
            delivery_unique = df['Delivery_person_ID'].nunique() 
            col1.metric('Entregadores unicos é:', delivery_unique )
     

        with col2: 
            avg = delivery_distance( df, fig=False)
            col2.metric( "A distancia média de todas as entregas é:", avg )


        with col3:
            df_aux1 = festival_analytics( df, 'Yes ', 'mean_time')
            col3.metric('Tempo médio\Festival é:', df_aux1 )
        



    with st.container():
        col1, col2, col3= st.columns( 3, gap='large') 

        with col1:
            df_aux1 = festival_analytics( df, 'Yes ', 'std_time' )
            col1.metric('Desvio Padrão do Festival é:', df_aux1 )


        with col2:
            df_aux1 = festival_analytics( df, 'No ', 'mean_time')
            col2.metric('Tempo médio\Festival é:', df_aux1 )


        with col3: 
            df_aux1 = festival_analytics( df, 'No ', 'std_time')
            col3.metric( 'Desvio Padrão do Festival é:', df_aux1 )

            
               

#=====================================================================================
  
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2= st.columns( 2, gap='large')


        with col1:   

            fig = delivery_distance(df, fig=True) 
            st.plotly_chart(fig, use_container_width=True ) 
             
        with col2:  
            #####GRÁFICO DE bigPIZZA- TEMPO MEDIO E DESVIO PADRAO  PARA CADA CIDADE E TRÁFEGO  
             
            fig = avg_mean_std_by_city_traffic( df )
            st.plotly_chart( fig, use_container_width=True ) 
        
#=====================================================================================    

    with st.container():
        #####GRÁFICO DE BARRAS - DISTÂNCIA MÉDIA DE CADA CIDADE
        st.markdown("""---""")
        st.title('Distribuição da distancia')
        col1, col2= st.columns( 2, gap='large')
        
        with col1: 
            fig = avg_std_time_graph(df)
            st.plotly_chart( fig, use_container_width=True )

            


        with col2:
            df_aux = df.loc[:, [ 'Time_taken(min)', 'Type_of_order' ,'City' ]].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['avg_distance', 'std_distance']
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width=True )
    
#===================================================================================== 
#                          THE END          
