# -*- coding: utf-8 -*-
import requests, sys
import datetime
import time
import operator
from operator import itemgetter
import datetime as dt
from tabulate import tabulate
from bs4 import BeautifulSoup

s = requests.session() #para pegar e manter a sessao

def pegarconteudo(url):
    aux = s.get(url)
    return str(aux.content)

def enviarconteudo(url,dados):
    aux = s.post(url,dados)
    return str(aux.content)



url = 'http://site.com.br/login'
#salva sessao inical
conteudo = pegarconteudo(url)
soup = BeautifulSoup(conteudo, 'html.parser')
token = soup.find('input', {'name': '_token'}).get('value')
dados = {'_token': token, 'email':'xxxxx', 'password' : 'xxxxxx'}
novo_conteudo = enviarconteudo(url,dados)


#fim
