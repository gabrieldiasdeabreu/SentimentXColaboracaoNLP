#!/usr/bin/env python
# coding: utf-8

# # Usando SentiStrength
# 
# ## Api do sentistrength

# In[1]:


'''requer plotly, pandas, requests, re e json'''
import plotly
import requests
import re
import json as Json
import pandas as pd
import time
# import matplotlib.pyplot as plt
# import numpy as np

import plotly.plotly as py
print(plotly.__version__)  # version >1.9.4 required
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout


# In[2]:


def arrumaQuery(query):
    ''' funcao auxiliar para arrumar a query'''
    return query.replace(' ', '+').replace('\n', '+')


# In[3]:


def get(url):
    try:
        return requests.get(url)
    except Exception:
        # sleep for a bit in case that helps
        time.sleep(1)
        # try again
        return get(url)


# In[4]:


def retornaSentimentoComSentiStrength(query):
    '''
    funcao que avalia os sentimentos utilizando 
    o SentiStrength retornando os 
    resultados posivitos e negativos
    '''
    BaseUrl =  "http://sentistrength.wlv.ac.uk"

    DOMAIN = "AutoDetect";
    SUBMIT = "Detect+Sentiment+in+Domain"
    
    # monta URL
    url = BaseUrl+'/results.php?domain='+DOMAIN+'&submit='+SUBMIT+'&text='+arrumaQuery(query)
    
#     print(url)
    #requisita
    r = get(url = url)
    
    # usa regex para capturar nota
    notaExpr = re.compile(r'has positive strength <b>.*</b> and negative strength <b>.*</b>')
    textoFiltrado = re.findall(notaExpr, str(r.content))
    pegaNotaPositiva = str(textoFiltrado).split('<b>')[1].split('</b>')[0]
    pegaNotaNegativa = str(textoFiltrado).split('<b>')[2].split('</b>')[0]
    
    return {'NotaPositiva':int(pegaNotaPositiva), 'NotaNegativa':int(pegaNotaNegativa)}


# In[5]:


# retornaSentimentoComSentiStrength('this is a horrible idea')


# In[6]:


# pd.DataFrame(columns=['autor', 'data', 'mensagem', 'NotaPos', 'NotaNeg'])
json = None
with open('exemplo.json', 'r') as arq:
    json = arq.read()
#     for commit in json.loads(arq.read()):
# #         print(commit)
#         nota = retornaSentimentoComSentiStrength(commit['mensagem'])
# #         print('autor:', commit['autor'])
# #         print('data:', commit['data'])
# #         print('mensagem:', commit['mensagem'])
# #         print('sentiment', nota)
#         dados.append([
#             commit['autor'],
#             commit['data'],
#             commit['mensagem'],
#             nota['NotaPositiva'],
#             nota['NotaNegativa']            
#         ])


# In[7]:


def converteJsonParaDataFrame(json):
    '''
    Recebe um Json represantando um commit com os campos 
    commit['autor'],
    commit['data'],
    commit['mensagem'] e retorna um DataFrame para análise
    '''
    i = 1
    dados = []
    for commit in Json.loads(json):
        print('Analisando a mensagem #'+str(i)+' :')
#         print(commit['mensagem'])
#         print('de : '+commit['autor'] + ' em '+ commit['data'])
#         print('mensagem : ' + str(i))
        nota = retornaSentimentoComSentiStrength(commit['mensagem'])
        dados.append([
            commit['autor'],
            commit['data'],
            commit['mensagem'],
            nota['NotaPositiva'],
            nota['NotaNegativa']            
        ])
        i+=1
    dados = pd.DataFrame(dados, columns=['autor', 'data', 'mensagem', 'NotaPos', 'NotaNeg'])
    dados.data = pd.to_datetime(dados.data)
    dados = dados.set_index('data')
    
    return dados


# In[8]:


def plotaGraficosSentimentoPorUsuario(dados):    
    # itera por cada usuário identificado no Json
    for grupo in dados.groupby('autor'):
        url = plotly.offline.plot({
            'data':[
                go.Bar(
                    x=grupo[1].index, # assign x as the dataframe column 'x'
                    y=grupo[1]['NotaPos'],
                    name='Positive Sentiment'
                ),
                go.Bar(
                    x=grupo[1].index, # assign x as the dataframe column 'x'
                    y=grupo[1]['NotaNeg'],
                    name='Negative Sentiment'
                )
            ],
            "layout": Layout(
                title=grupo[0],
                xaxis=dict(title='Commit Data'),
                yaxis=dict(title='Sentiment Polarity'),

            )
        }, filename='graphs/SentimentoDoColaborador_'+grupo[0]+'.html')


# In[9]:


# dados.sort_index()[['NotaPos','NotaNeg', 'mensagem', 'autor']].to_csv('saida_Codigo.csv')
# dados.describe().to_csv('analiseSaida.csv')


# In[10]:


def plotaGraficosSentimentoProjeto(dados, nomeProjeto):    
    # itera por cada usuário identificado no Json
#     for grupo in dados.groupby('autor'):
    url = plotly.offline.plot({
        'data':[
            go.Scatter(
                x=dados.index, # assign x as the dataframe column 'x'
                y=dados['NotaPos'],
                name='Positive Sentiment'
            ),
            go.Scatter(
                x=dados.index, # assign x as the dataframe column 'x'
                y=dados['NotaNeg'],
                name='Negative Sentiment'
            )
        ],
        "layout": Layout(
            title='Projeto: '+nomeProjeto,
            xaxis=dict(title='Commit Data'),
            yaxis=dict(title='Sentiment Polarity'),

        )
    }, filename='graphs/sentimentoDoProjetoAoLongoDoTempo.html')


# In[11]:


dados = converteJsonParaDataFrame(json)


# In[12]:


dados


# In[13]:


plotaGraficosSentimentoProjeto(dados, 'tensorflow')


# In[14]:


plotaGraficosSentimentoPorUsuario(dados)


# In[ ]:


# pandas>=0.23.4

