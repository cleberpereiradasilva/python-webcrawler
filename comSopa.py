from bs4 import BeautifulSoup
import requests, sys
from libs.funcoes import getContent, getTeta,dwContent
reload(sys)
sys.setdefaultencoding('utf8')


getContent = getContent('https://www.imdb.com/list/ls006318277/')
soup = BeautifulSoup(getContent, "lxml")
divs = soup.find_all("div", class_="lister-item mode-detail")
for div in divs:
    titulo = div.find("h3").find("a")
    codigoTeta = titulo['href'].split('/')[2]
    dv_img = div.find(class_='lister-item-image ribbonize')
    img_url = dv_img.find('img')['loadlate']
    destino = 'img/'+codigoTeta+'.jpg'
    feito = dwContent(img_url,destino)
    if(feito):
        print('Baixado com sucesso!')
    else:
        print('Erro ao baixar')









#fim
