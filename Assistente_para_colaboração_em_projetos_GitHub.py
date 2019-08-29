#!/usr/bin/env python
# coding: utf-8

# # Usando SentiStrength
# 
# ## Api do sentistrength

# In[1]:



'''requer plotly, pandas, requests, re e json'''
import plotly
import os
import requests
import re
import json as Json
import pandas as pd
import random as random
import time
import sys
# import matplotlib.pyplot as plt
# import numpy as np

import plotly.plotly as py
# print(plotly.__version__)  # version >1.9.4 required
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout
# !pip freeze > requirements.txt
nomeProjeto = sys.argv[1]
GITHUB_ID = sys.argv[2]
GITHUB_PASSWORD = sys.argv[3]

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
def printRequests(header):
    print('ainda tem '+ header['X-RateLimit-Remaining'] +' de '+ header['X-RateLimit-Limit']) 

def getCommits(nomeRepositorio):
    url = 'https://api.github.com/repos/'+nomeRepositorio+'/'+nomeRepositorio+'/commits?per_page=10'
    print(url)
    print('nadaaa')
    response = requests.get(url, auth=(GITHUB_ID, GITHUB_PASSWORD))
    resposta = Json.loads(response.content)
    printRequests(response.headers)
    jsonResultados = []
#     with open('jsonComCommitsDoRepositorio_'+nomeRepositorio, 'w') as result:
    i = 0 
    for r in resposta:
#             print(r)
        try:
            identificacao = r['author']['login']
        except:
            print("nao tem login")
        try:
            name = r['commit']['author']['name']
        except:
            print("nao tem nome") 
        try:
            email = r['commit']['author']['email']
        except:
            print("nao tem email") 
        msg = '\"'+r['commit']['message']+'\"'
        data = r['commit']['author']['date']
        requestStatus = requests.get(r['url'], auth=(GITHUB_ID, GITHUB_PASSWORD))
        printRequests(requestStatus.headers)
#             print(requestStatus.headers)
        stats = Json.loads(requestStatus.content)['stats']
        jsonResultados.append({'autor':identificacao,
                               'data':data,
                               'mod': stats['total'],
                               'adc': stats['additions'],
                               'rem': stats['deletions'],
                               'mensagem': msg})
        print('commit :'+str(i))
        i+=1
    return jsonResultados
#         json.dump(jsonResultados, result)    
    
# json = list()
# nomeArquivoJson = 'jsonComCommitsDoRepositorio_' + nomeProjeto
# with open(nomeArquivoJson, 'r') as arq:
#     file = arq.read()
#     json = Json.loads(file)
#     for linha in file.replace('\n',' ').split('PiperOrigin-RevId: '):
# #         iden = linha.split(',')[4]
#         split = linha[11:].split(',')
# #         print(split)
#         if split[0]!= '':
#             json.append(
#             {
#                 'autor': split[0],
#                 'data': split[1],
#                 'mod':split[2],
#                 'adc': split[3],
#                 'rem' : split[4],
#                 'mensagem': ','.join(split[5:])
#             })
        
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
# json


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
    for commit in json:
        print('Analisando a mensagem #'+str(i)+' :')
#         print(commit['mensagem'])
#         print('de : '+commit['autor'] + ' em '+ commit['data'])
#         print('mensagem : ' + str(i))
#         nota ={'NotaPositiva': random.randrange(1, 6),
#             'NotaNegativa':-1*random.randrange(1, 5)}
        nota = retornaSentimentoComSentiStrength(commit['mensagem'])
        dados.append([
            commit['autor'],
            commit['data'],
            commit['mensagem'],
            int(commit['mod']),
            commit['adc'],
            commit['rem'],
            nota['NotaPositiva'],
            nota['NotaNegativa']            
        ])
        i+=1
    dados = pd.DataFrame(dados, columns=['autor', 'data', 'mensagem','mod','adc','rem' , 'NotaPos', 'NotaNeg'])
    dados.data = pd.to_datetime(dados.data)
    dados = dados.set_index('data')
    dados['mod'] = (((dados['mod'] - dados['mod'].mean())/ dados['mod'].std())/(((dados['mod'] - dados['mod'].mean()) / dados['mod'].std()).max())) *5 
#     dados['adc'] = (dados['adc'] - dados['adc'].mean())/ dados['adc'].std()
    dados['adc'] = (((dados['adc'] - dados['adc'].mean())/ dados['adc'].std())/(((dados['adc'] - dados['adc'].mean()) / dados['adc'].std()).max())) *5 
    dados['rem'] = (((dados['rem'] - dados['rem'].mean())/ dados['rem'].std())/(((dados['rem'] - dados['rem'].mean()) / dados['rem'].std()).max())) *5 

#     dados['rem'] = (dados['rem'] - dados['rem'].mean())/ dados['rem'].std()
    
    return dados.sort_index()


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
                ),
                go.Scatter(
                    x=grupo[1].index, # assign x as the dataframe column 'x'
                    y=grupo[1]['mod'],
                    name='linhas modificadas'
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
            go.Bar(
                x=dados.index, # assign x as the dataframe column 'x'
                y=dados['NotaPos'],
                name='Positive Sentiment'
            ),
            go.Bar(
                x=dados.index, # assign x as the dataframe column 'x'
                y=dados['NotaNeg'],
                name='Negative Sentiment'
            ),
            go.Scatter(
                x=dados.index, # assign x as the dataframe column 'x'
                y=dados['mod'],
                name='linhas modificadas'
            )            
        ],
        "layout": Layout(
            title='Projeto: '+nomeProjeto,
            xaxis=dict(title='Commit Data'),
            yaxis=dict(title='Sentiment Polarity'),

        )
    }, filename='graphs/sentimentoDoProjetoAoLongoDoTempo.html')


# In[11]:


jsonCommits = getCommits(nomeProjeto)
dados = converteJsonParaDataFrame(jsonCommits)
os.mkdir('graphs')

# In[12]:


# dados


# In[13]:


plotaGraficosSentimentoProjeto(dados, nomeProjeto)


# In[14]:


plotaGraficosSentimentoPorUsuario(dados)


# In[15]:


# def plotaGraficosCalorProjeto(dados, nomeProjeto):    
#     # itera por cada usuário identificado no Json
# #     for grupo in dados.groupby('autor'):
#     dados[['mod','NotaPos', 'NotaNeg']].corr()
#     url = plotly.offline.plot({
#         'data':[
#             go.Heatmap(
#                 z= dados[['mod','NotaPos', 'NotaNeg']].corr(), 
                
# #                 yaxis = ['a', 'b', 'x'],
# #                 name='Positive Sentiment'                
#             ),                     
#         ],
#         "layout": Layout(
#             title='Correlação entre sentimento e produtividade: '+nomeProjeto,
            
# #             xaxis=dict(title='Commit Data'),
# #             yaxis=dict(title='Sentiment Polarity'),

#         )
#     }, filename='graphs/RelacaoCalorEntreVariaveis.html')


# In[ ]:





# In[16]:


# plotaGraficosCalorProjeto(dados, 'tensorflow')


# In[17]:


# dados['adc'] = (((dados['adc'] - dados['adc'].mean())/ dados['adc'].std())/(((dados['adc'] - dados['adc'].mean()) / dados['adc'].std()).max())) *5 
# dados['rem'] = (((dados['rem'] - dados['rem'].mean())/ dados['rem'].std())/(((dados['rem'] - dados['rem'].mean()) / dados['rem'].std()).max())) *5 


# In[18]:


# dados[['mod','NotaPos', 'NotaNeg']].corr()


# In[19]:


# go.Heatmapgl

