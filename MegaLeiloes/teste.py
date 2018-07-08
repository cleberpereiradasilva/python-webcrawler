# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, sys, os, errno
from libs.funcoes import dataehora, pegarconteudo, mkdir_p, baixar, baixarPDF
reload(sys)
sys.setdefaultencoding('utf8')

# começando, pegando a página principal de imóveis (somente com filtro de imoveis) e colocando ela em uma lista na 
# primeira posição


paginas = ["https://www.megaleiloes.com.br/imoveis?type=1"]

# criando um set para popular com as URLs individuais de cada imóvel

linksdosImoveis = set()

# vamos ciclar pela lista pagina que sera incrementada com novas paginas a medida que o bsoup for achando mais links 
# com "próxima pagina", quando ele não encontrar mais novas páginas ele vai breakar e já vamos ter coletado todos os links
# de todos os imóveis

for pagina in paginas:

	paginaInicial = pegarconteudo(pagina)

	soup = BeautifulSoup(paginaInicial, "lxml")

	finaldaspaginas = soup.find("li", class_="next disabled")

	miniaturas = soup.find_all("li", class_="item-row card success span3 ")



	for miniatura in miniaturas:
		linkdoImovel = miniatura.find("a", class_="card-image")
		linksdosImoveis.add(linkdoImovel['href']) 


	proximaPagina = soup.find("li", class_="next").find("a")

	proximaPagina = "https://www.megaleiloes.com.br" + proximaPagina["href"]

	paginas.append(proximaPagina)

	print (proximaPagina)
	print(linksdosImoveis)

	if finaldaspaginas != None:
		break

# definindo o diretório principal

diretorioArquivosImoveis = "imoveis/"

# transformando o set linksdosImoveis criado anteriormente para lista para poder selecionar posicoes dentro dele:

linksdosImoveis = list(linksdosImoveis)	

# pegando o código do imóvel baseado na URL, pegando os ultimos 6 digitos

codigoImovel = linksdosImoveis[1][-6:]

# carregando a pagina do imóvel no requests.get 

paginadoImovel = pegarconteudo(linksdosImoveis[1])

# carregando o requests.get da pagina do imovel no bsoup

soup = BeautifulSoup(paginadoImovel, "lxml")

# pegando os dados da página:

categoria = linksdosImoveis[1].split("/")[3].strip()
subcategoria = linksdosImoveis[1].split("/")[4].upper().strip()
tituloImovel = soup.find("h1", class_="page-header").text.strip()
statusImovel = soup.find("div", class_="span5").find("div").find("span").text
pracaImovel = soup.find("div", class_="span5").find("div").find("div", class_="pull-right").text
tipoImovel = soup.find("ul", class_="description").find("li").find("strong").text
leilaoImovel = soup.find("ul", class_="description").find_all("li")[1].text[8:]
lanceinicialImovel = soup.find("ul", class_="description").find_all("li")[2].text[15:]
ultimolanceImovel = soup.find("ul", class_="description").find_all("li")[3].text[14:]
incrementoImovel = soup.find("ul", class_="description").find_all("li")[4].text[12:]
localizacaoImovel = soup.find("ul", class_="description").find_all("li")[5].text[13:]
inicioImovel = soup.find("ul", class_="description").find_all("li")[6].text[8:]
terminoImovel = soup.find("ul", class_="description").find_all("li")[7].text[9:]
enderecoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[0].find("td").text
varaImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[1].find("td").text
forumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[2].find("td").text
numprocessoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").find("a").text
controlenumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").text[-8:]
autorImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[4].find("td").text
reuImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[5].find("td").text
descricaoImovel = soup.find("div", id="batch-description").text.strip()
valoravaliavaoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[7].text.split("}")[1].split("A descr")[0].strip()
editalImovelPDF = soup.find("div", id="buttons").find_all("a")[2]["href"]
nomedoarquivoEditalPDF = editalImovelPDF.split("/")[6]
laudoImovelPDF = soup.find("div", id="buttons").find_all("a")[3]["href"]
nomedoarquivoLaudoPDF = laudoImovelPDF.split("/")[6]
matriculaImovelPDF = soup.find("div", id="buttons").find_all("a")[4]["href"]
nomedoarquivoMatriculaPDF = matriculaImovelPDF.split("/")[6]

# Printando o que foi coletado somente para verificação

print("")
print(tituloImovel)
print(categoria)
print(subcategoria)
print(statusImovel)
print(pracaImovel)
print(tipoImovel)
print(leilaoImovel)
print(lanceinicialImovel)
print(ultimolanceImovel)
print(incrementoImovel)
print(localizacaoImovel)
print(inicioImovel)
print(terminoImovel)
print(enderecoImovel)
print(varaImovel)
print(forumImovel)
print(numprocessoImovel)
print(controlenumImovel)
print(autorImovel)
print(reuImovel)
print(descricaoImovel)
print(valoravaliavaoImovel)
print(editalImovelPDF)

print ("")

# definindo o diretório do imóvel para salvar os arquivos:


diretorioDoImovel = str(diretorioArquivosImoveis) + str(subcategoria) + "/" + str(codigoImovel) + "/"

# criando os diretórios necessários para os arquivos do imóvel:

try:
    mkdir_p(diretorioDoImovel)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# baixando os pdfs do imóvel:


baixarPDF(editalImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoEditalPDF))
baixarPDF(laudoImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoLaudoPDF))
baixarPDF(matriculaImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoMatriculaPDF))







