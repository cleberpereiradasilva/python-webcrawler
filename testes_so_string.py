# -*- coding: utf-8 -*-
#today:
# split
# replace
# defs(funcoes)
# pacotes(pastas com __init__.py)
# request(get from web)
# loop nos elementos
# remover item de lista
# substrings direita[:15]/direita[15:], direita[2:5]....

import requests, sys
from libs.funcoes import getContent, getTeta
reload(sys)
sys.setdefaultencoding('utf8')

def principal():
    pageContent = getContent('https://www.imdb.com/list/ls006318277/')
    aux = pageContent.split('lister-list')
    if(len(aux) == 2): # verificar se vieram as partes que esperavamos
        meio = aux[1].split('footer filmosearch')[0]
        divs = meio.split('lister-item mode-detail')
        del divs[0] # remove o primeiro item que eh invalido para nos....
        contador = 1
        for div in divs:
                #div = divs[1]
                links = div.split('<a href')
                codigoTeta = links[0].split('"')[4]
                titulo = links[2].replace('<','>').split('>')[1]
                print(str(contador)+': '+titulo)
                print('\tPopularide: '+getTeta(codigoTeta))
                contador = contador + 1

def alternativa():
    pageContent = getContent('https://www.imdb.com/list/ls006318277/')
    aux = pageContent.split('lister-list')
    if(len(aux) == 2): # verificar se vieram as partes que esperavamos
        meio = aux[1].split('footer filmosearch')[0]
        divs = meio.split('lister-item mode-detail')
        del divs[0] # remove o primeiro item que eh invalido para nos....
        contador = 1
        for div in divs:
                #div = divs[1]
                links = div.split('<a href')
                codigoTeta = links[0].split('"')[4]
                titulo = links[2].replace('<','>').split('>')[1]
                print(str(contador)+': '+titulo)
                print('\tPopularide: '+getTeta(codigoTeta))
                contador = contador + 1

principal()






#print(direita[:15])

# if( 'lister-list' in str(page.content)):
#     print('Tem')
#print(page.content)
