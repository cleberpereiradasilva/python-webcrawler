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

print(linksdosImoveis[1])

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
linkprocessoImovel = soup.find("div", class_="span9").find("a")["href"]
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
contratoImovel = soup.find("textarea", id="contract").text
localimagemImovel = soup.find("div", class_="span7").find("div", class_="carousel slide")



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
diretorioDasImagens = str(diretorioDoImovel) + "imagens/"

# criando os diretórios necessários para os arquivos do imóvel:

try:
    mkdir_p(diretorioDoImovel)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# criando diretório para as imagens        

try:
    mkdir_p(diretorioDoImovel + "imagens/")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Se tiver uma única imagem baixar essa única imagem, se tiver mais de uma entao baixar todas:

if localimagemImovel is None:
	imagemImovel = soup.find("img", class_="batch-image")["src"]
	nomeFoto = imagemImovel.split("/")[6]
	baixar(imagemImovel,str(diretorioDasImagens) + str(nomeFoto))
else:
	multiplasFotos = localimagemImovel.find_all("img")
	for cadafoto in multiplasFotos:
		caminhoImagem = cadafoto["src"]
		nomeFoto = caminhoImagem.split("/")[6]
		print (caminhoImagem)
		print (nomeFoto)
		baixar(caminhoImagem, str(diretorioDasImagens) + str(nomeFoto))



# baixando os pdfs do imóvel:


baixarPDF(editalImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoEditalPDF))
baixarPDF(laudoImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoLaudoPDF))
baixarPDF(matriculaImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoMatriculaPDF))


# Gravando dados em .txt:

f= open(str(diretorioDoImovel) + str(codigoImovel) + ".txt" ,"w+")
f.write("Categoria: " + categoria + "\n")
f.write("Sub-Categoria: " + subcategoria + "\n")
f.write("Titulo do Imóvel: " + tituloImovel + "\n")
f.write("Status: " + statusImovel + "\n")
f.write("Praça: " + pracaImovel + "\n")
f.write("Tipo: " + tipoImovel + "\n")
f.write("Leilão: " + leilaoImovel + "\n")
f.write("Lance Inicial: " + lanceinicialImovel + "\n")
f.write("Último Lance: " + ultimolanceImovel + "\n")
f.write("Incremento: " + incrementoImovel + "\n")
f.write("Localização: " + localizacaoImovel + "\n")
f.write("Início: " + inicioImovel + "\n")
f.write("Término: " + terminoImovel + "\n")
f.write("Endereço: " + enderecoImovel + "\n")
f.write("Vara: " + varaImovel + "\n")
f.write("Fórum: " + forumImovel + "\n")
f.write("Número do processo: " + numprocessoImovel + "\n")
f.write("Link do processo:: " + linkprocessoImovel + "\n")
f.write("Controle nº: " + controlenumImovel + "\n")
f.write("Autor: " + autorImovel + "\n")
f.write("Réu: " + reuImovel + "\n")
f.write("Valor de Avaliação: " + valoravaliavaoImovel)
f.write("Descrição: " + descricaoImovel + "\n")
f.close()






