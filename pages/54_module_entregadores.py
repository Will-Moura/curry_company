

# BIBLIOTECAS 
import pandas as pd 
import re 
import plotly.express as px
import streamlit as st
from PIL import Image
import folium

from streamlit_folium import folium_static
    
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

def aval_mean_traffic( df ):
                #agrupamento para analisar
                df_avl_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                        .groupby('Road_traffic_density')
                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
                #mudança de nome das colunas
                df_avl_by_traffic.columns = ['mean_of_delivery', '(desvio_padrão)']
                #reset index 
                df_avl_by_traffic.reset_index()
                return df_avl_by_traffic


def aval_mean_by_clima( df ):
                st.markdown( '###### Avaliação média por clima' ) 
                aval_by_clima = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                        .groupby('Weatherconditions')
                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
                #mudando o nome dos index:
                aval_by_clima.columns = ['média', "desvio_padrão"] 
                #resetando indexe visualizando:
                aval_by_clima.reset_index()
                return aval_by_clima

def top_delivery( df , which_ascending ):
                df1 = (   df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']] 
                                                                .groupby(['City','Delivery_person_ID']) 
                                                                .mean().sort_values( ['City','Time_taken(min)'], ascending=which_ascending)
                                                                .reset_index()  )

                df_aux1 = df1.loc[df1['City'] == 'Metropolitian ', :].head(10)
                df_aux2 = df1.loc[df1['City'] == 'Urban ', :].head(10) 
                df_aux3 = df1.loc[df1['City'] == 'Semi-Urban ', :].head(10)

                df2 = pd.concat([df_aux1, df_aux2, df_aux3 ]).reset_index(drop=True)
                return df2

#----------------------- INICIO DA ESTRUTURA LÓGICA ---------------------
#=====================================================================================
# IMPORTANDO DATASET
#=====================================================================================
#df = pd.read_csv(r'C:\Users\Administrador\Documents\repos\03_FTC\FTC_PROJETOS\analise_com_streamlit\dataset\train.csv')
df = pd.read_csv('dataset\train.csv')
#=====================================================================================
# LIMPANDO DADOS
#=====================================================================================
df = clean_code (df) 



#=====================================================================================
#BARRA LATERAL esquerda)
#===================================================================================== 

#textos
st.header( 'Visão Entregadores' ) 

#imagem
#image_path = 'C:\\Users\\Administrador\\Documents\\repos\\03_FTC\\FTC_PROJETOS\\analise_com_streamlit\\imagem_ds1.png'
image = Image.open( 'imagem1.png' )
st.sidebar.image( image, width=120 ) 



#textos
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' ) 
st.sidebar.markdown( """---""") 


#=====================================================================================
# Criando um slider e uma seleção
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
#FILTROS
#===================================================================================== 
#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :] 

#Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#=====================================================================================
#LAYOUT dos GRÁFICOS
#===================================================================================== 

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])
 
with tab1: 
    with st.container(): 
        st.markdown( '### Todas as Métricas' )
                     # (gap='large=distancia entre as colunas)
        col1, col2, col3, col4 = st.columns( 4, gap='large') 
        with col1:  
            #maior idade dos entregadores: 
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric( "Maior idade:", maior_idade )

        with col2:  
            #menor idade dos entregadores:
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric( "Menor idade:", menor_idade )

        with col3:
            #Melhor condição:
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max() 
            col3.metric( 'Melhor condição:', melhor_condicao)

        with col4: 
            #Pior idade: 
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição:', pior_condicao)


    with st.container(): 
        st.markdown("---")
        st.markdown( '### Avaliações' ) 

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '###### Avaliação media por entregador' ) 
            df_ratings_by_delivery_ID = (df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby 
                                                    ('Delivery_person_ID').mean().reset_index())
            st.dataframe(df_ratings_by_delivery_ID)



        with col2: 
            st.markdown( '###### Avaliação média por trânsito' )
            df_avl_by_traffic = aval_mean_traffic( df )
            st.dataframe( df_avl_by_traffic )    

####
            st.markdown("""---""")
####

            aval_by_clima = aval_mean_by_clima( df )
            st.dataframe( aval_by_clima )

            
                           
    with st.container():
        st.markdown("""---""")
        st.markdown( '### Tempo por entrega' )

        col1, col2 = st.columns( 2 )
          
        with col1: 
            st.markdown('###### Top entregadores mais rápidos')
            df2 = top_delivery( df, which_ascending=True )
            st.dataframe(df2) 

            

        with col2:  
            st.markdown('###### Top entregadores mais lentos')

            df2 =  top_delivery( df , which_ascending=False)
            st.dataframe( df2 )
             
            


        