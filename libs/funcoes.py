import requests
def dwContent(url, destino):
    try:
        r = requests.get(url)
        open(destino, 'wb').write(r.content)
        return True
    except:
        return False

def getContent(url):
    page = requests.get(url)
    return str(page.content)

def getTeta(codigoTeta):
    pageContent = getContent('https://www.imdb.com/title/'+str(codigoTeta))
    aux = pageContent.split('titleOverviewSprite')
    popularidade = 'N/D'
    if(len(aux) == 5):
        esquerda = aux[3].replace('(','>').split('>')
        popularidade = esquerda[-2].strip()
    return str(popularidade).strip()
