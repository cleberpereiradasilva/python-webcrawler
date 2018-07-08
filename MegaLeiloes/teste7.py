# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from  more_itertools import unique_everseen
import requests, sys, os, errno, mysql.connector, datetime, time, collections
from libs.funcoes import dataehora, pegarconteudo, mkdir_p, baixar, baixarPDF, procurarOutrosLotes
reload(sys)
sys.setdefaultencoding('utf8')

# dados da base que vamos alimentar

db_usuario = "python"
db_senha = "contem1kg"
db_host = "127.0.0.1"
db_nomebase = "python"

inicioExecucaoScript = datetime.datetime.now()


# começando, pegando a página principal de imóveis (somente com filtro de imoveis) e colocando ela em uma lista na 
# primeira posição

paginas = ["https://www.megaleiloes.com.br/imoveis?type=1"]

# criando um set para popular com as URLs individuais de cada imóvel

linksdosImoveis = set()

# criando uma lista para popular com as URLs adicionais (de lotes) encontradas dentro de cada pagina de imovel



# vamos ciclar pela lista pagina que sera incrementada com novas paginas a medida que o bsoup for achando mais links 
# com "próxima pagina", quando ele não encontrar mais novas páginas ele vai breakar e já vamos ter coletado todos os links
# de todos os imóveis

for pagina in paginas:

	# carregando a pagina no requests.get

	paginaInicial = pegarconteudo(pagina)

	# carregando a pagina no soup

	soup = BeautifulSoup(paginaInicial, "lxml")

	# tentando encontrar a tag que vai me indicar que chegou na ultima pagina de listagem de imoveis

	finaldaspaginas = soup.find("li", class_="next disabled")

	# buscando com o soup todos os links dos imoveis em cada pagina de listagem de imoveis

	miniaturas = soup.find("ul", class_="thumbnails").find_all("li", class_="item-row")

	# fazendo um loop para puxar o href de cada pagina de imovel na pagina de listagem de imoveis

	for miniatura in miniaturas:
		linkdoImovel = miniatura.find("a", class_="card-image")
		linksdosImoveis.add(linkdoImovel['href']) 


	#  buscando o link da proxima pagina para adicionar a minha lista de paginas

	proximaPagina = soup.find("li", class_="next").find("a")

	proximaPagina = "https://www.megaleiloes.com.br" + proximaPagina["href"]

	# adicionando a proxima pagina a minha lista de paginas

	paginas.append(proximaPagina)

	print (proximaPagina)
	print(len(linksdosImoveis))

	# verificando se o final das paginas já foi encontrado, se sim então breaka

	if finaldaspaginas != None:
		break


# definindo o diretório principal

diretorioArquivosImoveis = "imoveis/"

# transformando o set linksdosImoveis criado anteriormente para lista para poder selecionar posicoes dentro dele:

linksdosImoveis = list(linksdosImoveis)	

print (type(linksdosImoveis))

# Fazendo um set para colocar o código de todos os imoveis que ja foram scrapeados

codigosScrapeados = set()

# iniciando loop para coletar os dados dos imoveis

contadorFor = 0

for paginadeimovel in linksdosImoveis:

	contadorFor = contadorFor + 1

	# pegando o código do imóvel baseado na URL, pegando os ultimos 6 digitos

	print ("")

	# print(paginadeimovel)

	print ("Total de itens linksdosImoveis: "),

	print (len(linksdosImoveis))

	print ("Quantidade de itens percorridos neste for: "),

	print (contadorFor)

#	print ("Encontrou algum item duplicado no paginadeimovel? ")	

#	print [item for item, count in collections.Counter(list(paginadeimovel)).items() if count > 1]

	codigoImovel = paginadeimovel.split("?")[0][-6:]

	print ("")

	print(codigoImovel)

	print ("")

	# começa carregando a pagina do imóvel no requests.get 

	requestsPaginadoImovel = pegarconteudo(paginadeimovel)

	# print(paginadeimovel)

	# print ("")

	# carregando o requests.get da pagina do imovel no bsoup

	soup = BeautifulSoup(requestsPaginadoImovel, "lxml")

	# evitando duplicatas
	# se o codigo estiver no set

	if codigoImovel in codigosScrapeados:

		# e se o codigo estiver no set e a url tiver "?pagina=":
	
		if len(paginadeimovel.split("?")) > 1:

			# somente pegar as paginas dos lotes e salvar na outrosLotes, nao coletar nenhum dado do imovel e nao salvar nada

			procurarOutrosLotes(soup,linksdosImoveis)

			linksdosImoveis = list (unique_everseen(linksdosImoveis))

	# se o codigo não estiver no set				
	else:

		procurarOutrosLotes(soup,linksdosImoveis)

		linksdosImoveis = list (unique_everseen(linksdosImoveis))

		# adicionar o codigo ao set
		codigosScrapeados.add(codigoImovel)

		# coletar dados e fazer tudo

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
			print (imagemImovel)

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

print ("")
print ("Lista de imoveis percorridos:")
print (sorted(linksdosImoveis))
print ("Concluído")
print ("Inicio: "),
print (inicioExecucaoScript)
terminoExecucaoScript = datetime.datetime.now()
print ("Término: "),
print (terminoExecucaoScript)
print ("Total de itens linksdosImoveis: "),
print (len(linksdosImoveis))
print ("Quantidade de itens percorridos no for: "),
print (contadorFor)

