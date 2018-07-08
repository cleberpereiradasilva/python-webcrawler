# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from  more_itertools import unique_everseen
import requests, sys, os, errno, mysql.connector
from libs.funcoes import dataehora, pegarconteudo, mkdir_p, baixar, baixarPDF
reload(sys)
sys.setdefaultencoding('utf8')


db_usuario = "python"
db_senha = "contem1kg"
db_host = "127.0.0.1"
db_nomebase = "python"


# começando, pegando a página principal de imóveis (somente com filtro de imoveis) e colocando ela em uma lista na 
# primeira posição

paginas = ["https://www.megaleiloes.com.br/imoveis?type=1"]

# criando um set para popular com as URLs individuais de cada imóvel

linksdosImoveis = set()

outrosLotes = []

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

print (type(linksdosImoveis))

for paginadeimovel in linksdosImoveis:

	# pegando o código do imóvel baseado na URL, pegando os ultimos 6 digitos

	print ("")

	print(paginadeimovel)

	codigoImovel = paginadeimovel.split("?")[0][-6:]

	print ("")

	print(codigoImovel)


	# carregando a pagina do imóvel no requests.get 

	paginadoImovel = pegarconteudo(paginadeimovel)

	print(paginadeimovel)

	# carregando o requests.get da pagina do imovel no bsoup

	soup = BeautifulSoup(paginadoImovel, "lxml")

	# pegando os dados da página:

	categoria = paginadeimovel.split("/")[3].strip()
	subcategoria = paginadeimovel.split("/")[4].upper().strip()
	tituloImovel = soup.find("h1", class_="page-header").text.strip()
	
	try:
		statusImovel = soup.find("div", class_="span5").find("div").find("span").text
	except:
		pass

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
	descricaoImovel = soup.find("div", id="batch-description").text.strip()
	try:
		editalImovelPDF = soup.find("div", id="buttons").find_all("a")[2]["href"]
	except:
		pass

	nomedoarquivoEditalPDF = editalImovelPDF.split("/")[6]

	try:
		laudoImovelPDF = soup.find("div", id="buttons").find_all("a")[3]["href"]
	except:
		pass

	nomedoarquivoLaudoPDF = laudoImovelPDF.split("/")[6]
	contratoImovel = soup.find("textarea", id="contract").text
	localimagemImovel = soup.find("div", class_="span7").find("div", class_="carousel slide")

	if tipoImovel == "Leilão Judicial":
		forumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[2].find("td").text
		varaImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[1].find("td").text
		numprocessoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").find("a").text
		controlenumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").text[-8:]
		linkprocessoImovel = soup.find("div", class_="span9").find("a")["href"]
		autorImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[4].find("td").text
		reuImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[5].find("td").text
		valoravaliavaoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[7].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()
		try:
			matriculaImovelPDF = soup.find("div", id="buttons").find_all("a")[4]["href"]
		except:
			pass

		nomedoarquivoMatriculaPDF = matriculaImovelPDF.split("/")[6]

	if tipoImovel == "Leilão Extrajudicial":
		comitenteImovel = soup.find("div", class_="span9").find_all("tr")[1].find("td").text
		try:
			valoravaliavaoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()
		except: 
  			pass


# 2:55am - aqui embaixo eu tentei fazer um jeito para pegar os links dos lotes adicionais dentro de cada imovel só que do jeito
# que eu fiz não vai dar certo porque eu to transformando a lista em set e depois de volta em lista e quando eu faço isso eu
# perco a ordem da lista obviamente e vou ficar em um loop eterno   			
#
# 8:42am - descobri essa funcao na library more_itertools do python que limpa duplicatas em uma lista visando performance, chama 
# unique_everseen(), https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
# então ao inves de transformar a lista que eu vou somar a lista do for em set e perder a ordem aqui embaixo, eu agora 
# mantenho ela como lista e rodo o o unique_everseen() para manter os itens unicos e somo essa lista com a lista do loop
# 

  	try:

	  	auxOutrosLotes = soup.find("div", id="batches-list-min").find_all("a")

	  	print ("O tipo do auxOutrosLotes é:"),
	  	print (type(auxOutrosLotes))

	  	for lote in auxOutrosLotes:


	  		# 2:45 - problema, remover os ultimos 9 caracteres do href abaixo vai tirar o ?pagina=1 da URL
	  		# e assim não vamos acessar as outras paginas com mais botoes para clicar e por no set
	  		# se eu mandar com ?pagina=1 vamos quebrar a leitura do código na variavel codigoImovel 
	  		# - RESOLVIDO - fiz isso com a codigoImovel: codigoImovel = paginadeimovel.split("?")[0][-6:]

	  		outrosLotes.extend(["https://www.megaleiloes.com.br" + lote["href"]])

	  	print ("")

	  	print ("Outros lotes:")

	  	print (outrosLotes)


	  	print ("Tipo dos outros lotes:")

	  	print (type(outrosLotes))

	  	outrosLotes = list (unique_everseen(outrosLotes))
	  	
	  	print ("")

	  	print ("Tipo dos outros lotes depois de ficar unico:")

	  	print (type(outrosLotes))

	  	linksdosImoveis.extend(outrosLotes)

	  	# Vamos limpar a outrosLotes depois de te-la adicionado a linksdosImoveis

	  	outrosLotes=[]

	  	linksdosImoveis = list (unique_everseen(linksdosImoveis))

	  	print ("")

	  	print ("linksdosImoveis extendida com Outros lotes")

	  	print (linksdosImoveis)

	except:
		pass




	# Printando o que foi coletado somente para verificação
	# print("")
	# print(tituloImovel)
	# print(categoria)
	# print(subcategoria)
	# print(statusImovel)
	# print(pracaImovel)
	# print(tipoImovel)
	# print(leilaoImovel)
	# print(lanceinicialImovel)
	# print(ultimolanceImovel)
	# print(incrementoImovel)
	# print(localizacaoImovel)
	# print(inicioImovel)
	# print(terminoImovel)
	# print(enderecoImovel)
	# print(varaImovel)
	# print(forumImovel)
	# print(numprocessoImovel)
	# print(controlenumImovel)
	# print(autorImovel)
	# print(reuImovel)
	# print(descricaoImovel)
	# print(valoravaliavaoImovel)
	# print(editalImovelPDF)
	# print ("")

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


	# Criando a lista para adicionar as imagens para o banco

	imagensparaBanco = []

	# Se tiver uma única imagem baixar essa única imagem, se tiver mais de uma entao baixar todas:


	if localimagemImovel is None:
		imagemImovel = soup.find("img", class_="batch-image")["src"]
		nomeFoto = imagemImovel.split("/")[6]
		baixar(imagemImovel,str(diretorioDasImagens) + str(nomeFoto))

		imagensparaBanco.extend([imagemImovel])

	else:
		multiplasFotos = localimagemImovel.find_all("img")

		for cadafoto in multiplasFotos:
			caminhoImagem = cadafoto["src"]

			imagensparaBanco.extend([caminhoImagem])

			nomeFoto = caminhoImagem.split("/")[6]
			print (caminhoImagem)
			print (nomeFoto)
			baixar(caminhoImagem, str(diretorioDasImagens) + str(nomeFoto))



	# baixando os pdfs do imóvel:


	try: 
		baixarPDF(editalImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoEditalPDF))
	except:
		pass
	try: 
		baixarPDF(laudoImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoLaudoPDF))
	except:
		pass
	
	if tipoImovel == "Leilão Judicial":
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
	if tipoImovel == "Leilão Judicial":
		f.write("Vara: " + varaImovel + "\n")
		f.write("Fórum: " + forumImovel + "\n")
		f.write("Número do processo: " + numprocessoImovel + "\n")
		f.write("Link do processo:: " + linkprocessoImovel + "\n")
		f.write("Controle nº: " + controlenumImovel + "\n")
		f.write("Autor: " + autorImovel + "\n")
		f.write("Réu: " + reuImovel + "\n")
	if tipoImovel == "Leilão Extrajudicial":
		f.write("Comitente: " + comitenteImovel + "\n")
	try:	 
		f.write("Valor de Avaliação: " + valoravaliavaoImovel + "\n")
	except:
		pass
	f.write("Descrição: " + descricaoImovel + "\n")
	f.close()

	# Verificando se algumas variaveis existem e se nao existem adicionando valor vazio a elas:

	if 'varaImovel' not in locals():
		varaImovel = "N/D"
	
	if 'forumImovel' not in locals():
		forumImovel = "N/D"	
	
	if 'numprocessoImovel' not in locals():
		numprocessoImovel = "N/D"

	if 'linkprocessoImovel' not in locals():
		linkprocessoImovel = "N/D"

	if 'controlenumImovel' not in locals():
		controlenumImovel = "N/D"

	if 'autorImovel' not in locals():
		autorImovel = "N/D"				

	if 'reuImovel' not in locals():
		reuImovel = "N/D"		

	if 'comitenteImovel' not in locals():
		comitenteImovel = "N/D"		

	if 'valoravaliavaoImovel' not in locals():
		valoravaliavaoImovel = "N/D"	

	if 'valoravaliavaoImovel' not in locals():
		valoravaliavaoImovel = "N/D"

	if 'matriculaImovelPDF' not in locals():
		matriculaImovelPDF = "N/D"

	if 'laudoImovelPDF' not in locals():
		laudoImovelPDF = "N/D"

	if 'editalImovelPDF' not in locals():
		editalImovelPDF = "N/D"

	# Fazendo insert dos dados no banco de dados

	connector = mysql.connector.connect(user=db_usuario, password=db_senha, host=db_host, database=db_nomebase,
	                                            buffered=True)
	cursor = connector.cursor()

	queryInserirDadosBanco = 'INSERT INTO megaleiloes (titulo, categoria, subcategoria, status, praca, tipo, leilao, lance_inicial, ultimo_lance, incremento, localizacao, inicio, termino, endereco, comitente, vara, forum, num_processo, link_processo, controle_num, autor, reu, descricao, valor_avaliacao, edital, laudo_avaliacao, matricula, mapa, imagens) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

	# 'INSERT INTO megaleiloes (titulo, categoria, subcategoria, status, praca, tipo, leilao, lance_inicial, ultimo_lance, incremento, localizacao, inicio, termino, endereco, comitente, vara, forum, num_processo, link_processo, controle_num, autor, reu, descricao, valor_avaliacao, edital, laudo_avaliacao, matricula, mapa, imagens) VALUES (' + str(tituloImovel.strip()) + ', ' +  categoria + ', ' + subcategoria + ', ' + statusImovel + ', ' + pracaImovel + ', ' + tipoImovel + ', ' + leilaoImovel + ', ' + lanceinicialImovel + ', ' + ultimolanceImovel + ', ' + incrementoImovel + ', ' + localizacaoImovel + ', ' + inicioImovel + ', ' + terminoImovel + ', ' + enderecoImovel + ', ' + comitenteImovel + ', ' + varaImovel + ', ' + forumImovel + ', ' + numprocessoImovel + ', ' + linkprocessoImovel + ', ' + controlenumImovel + ', ' + autorImovel + ', ' + reuImovel + ', ' + descricaoImovel.strip() + ', ' + valoravaliavaoImovel + ', ' + editalImovelPDF + ', ' + laudoImovelPDF + ', ' + matriculaImovelPDF + ', ' + enderecoImovel + ', ' + str(imagensparaBanco) + ');'	

	cursor.execute(queryInserirDadosBanco, (tituloImovel, categoria, subcategoria, statusImovel, pracaImovel, tipoImovel, leilaoImovel, lanceinicialImovel, ultimolanceImovel, incrementoImovel, localizacaoImovel, inicioImovel, terminoImovel, enderecoImovel, comitenteImovel, varaImovel, forumImovel, numprocessoImovel, linkprocessoImovel, controlenumImovel, autorImovel, reuImovel, descricaoImovel.strip(), valoravaliavaoImovel, editalImovelPDF, laudoImovelPDF, matriculaImovelPDF, enderecoImovel, str(imagensparaBanco)))

	connector.commit()
	connector.close()
	cursor.close()



