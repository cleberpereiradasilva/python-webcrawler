# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, sys, os, errno, datetime, time, collections,mysql.connector
from libs.funcoes import dataehora, pegarconteudo, mkdir_p, baixarimagem, baixarPDF, procurarOutrosLotes
reload(sys)
sys.setdefaultencoding('utf8')

# dados da base que vamos alimentar

db_usuario = "root"
db_senha = "2323"
db_host = "127.0.0.1"
db_nomebase = "mega"
connector = None

inicioExecucaoScript = datetime.datetime.now()

#TODO colocar mais categorias
categorias = ['apartamentos']

# começando, pegando a página principal de imóveis (somente com filtro de imoveis) e colocando ela em uma lista na 
# primeira posição


def obterDados(paginadeimovel):
	requestsPaginadoImovel = pegarconteudo(paginadeimovel)
	# carregando o requests.get da pagina do imovel no bsoup
	soup = BeautifulSoup(requestsPaginadoImovel[0], "lxml")
	retorno = {}
	retorno['codigoImovel'] = paginadeimovel.split("-")[-1]
	print(retorno['codigoImovel'])

	retorno['status_code'] = int(requestsPaginadoImovel[1])	
	retorno['varaImovel'] = "N/D"
	retorno['forumImovel'] = "N/D" 
	retorno['numprocessoImovel'] = "N/D"
	retorno['linkprocessoImovel'] = "N/D"
	retorno['controlenumImovel'] = "N/D"
	retorno['autorImovel'] = "N/D"      
	retorno['reuImovel'] = "N/D"       
	retorno['comitenteImovel'] = "N/D" 
	retorno['valoravaliavaoImovel'] = "N/D"    
	retorno['valoravaliavaoImovel'] = "N/D"
	retorno['matriculaImovelPDF'] = "N/D"
	retorno['laudoImovelPDF'] = "N/D"
	retorno['editalImovelPDF'] = "N/D"

	if retorno['status_code'] != 404:
		retorno['partecomLotes'] = soup.find("div", id="batches-list")		
		retorno['tituloImovel'] = soup.find("h1", class_="page-header").text.strip()
		try:
		    retorno['statusImovel'] = soup.find("div", class_="span5").find("div").find("span").text
		except:
		    pass
		retorno['pracaImovel'] = soup.find("div", class_="span5").find("div").find("div", class_="pull-right").text
		retorno['tipoImovel'] = soup.find("ul", class_="description").find("li").find("strong").text
		retorno['leilaoImovel'] = soup.find("ul", class_="description").find_all("li")[1].text[8:]
		retorno['lanceinicialImovel'] = soup.find("ul", class_="description").find_all("li")[2].text[15:]
		retorno['ultimolanceImovel'] = soup.find("ul", class_="description").find_all("li")[3].text[14:]
		retorno['incrementoImovel'] = soup.find("ul", class_="description").find_all("li")[4].text[12:]
		retorno['localizacaoImovel'] = soup.find("ul", class_="description").find_all("li")[5].text[13:]
		retorno['inicioImovel'] = soup.find("ul", class_="description").find_all("li")[6].text[8:]
		retorno['terminoImovel'] = soup.find("ul", class_="description").find_all("li")[7].text[9:]
		retorno['enderecoImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[0].find("td").text
		retorno['descricaoImovel'] = soup.find("div", id="batch-description").text.strip()
		try:
		    retorno['editalImovelPDF'] = soup.find("div", id="buttons").find_all("a")[2]["href"]
		    retorno['nomedoarquivoEditalPDF'] = retorno['editalImovelPDF'].split("/")[6]
		except:
		    pass
		try:
		    retorno['laudoImovelPDF'] = soup.find("div", id="buttons").find_all("a")[3]["href"]
		    retorno['nomedoarquivoLaudoPDF'] = retorno['laudoImovelPDF'].split("/")[6]
		except:
		    pass
		try:
		    retorno['matriculaImovelPDF'] = soup.find("div", id="buttons").find_all("a")[4]["href"]
		    retorno['nomedoarquivoMatriculaPDF'] = retorno['matriculaImovelPDF'].split("/")[6]
		except:
		    pass
		retorno['contratoImovel'] = soup.find("textarea", id="contract").text

		retorno['localimagemImovel'] = soup.find("div", class_="span7").find("div", class_="carousel slide")

		retorno['forumImovel'] = "N/D"
		retorno['varaImovel'] = "ND"
		retorno['orumImovel'] = "ND"
		retorno['varaImovel'] = "ND"
		retorno['numprocessoImovel'] = "ND"
		retorno['controlenumImovel'] = "ND"
		retorno['linkprocessoImovel'] = "ND"
		retorno['autorImovel'] = "ND"
		retorno['reuImovel'] = "ND"
		retorno['valoravaliavaoImovel'] = "ND"


		if retorno['tipoImovel'] == "Leilão Judicial":
		    retorno['forumImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[2].find("td").text
		    retorno['varaImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[1].find("td").text
		    retorno['numprocessoImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").find("a").text
		    retorno['controlenumImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").text[-8:]
		    retorno['linkprocessoImovel'] = soup.find("div", class_="span9").find("a")["href"]
		    retorno['autorImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[4].find("td").text
		    retorno['reuImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[5].find("td").text
		    retorno['valoravaliavaoImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[7].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()

		retorno['comitenteImovel'] = "N/D"           

		if retorno['tipoImovel'] == "Leilão Extrajudicial":
		    retorno['comitenteImovel'] = soup.find("div", class_="span9").find_all("tr")[1].find("td").text
		    try:
		        retorno['valoravaliavaoImovel'] = soup.find("table", class_="table table-nomargin").find_all("tr")[3].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()
		    except: 
		        pass

	return retorno		 

def getFromUrl():


def getCursor():
	global connector
	connector = mysql.connector.connect(user=db_usuario, 
			password=db_senha, 
			host=db_host, 
			database=db_nomebase,
			buffered=True)
	return connector.cursor()

def existeRegistro(chave):		
	cursor = getCursor()
	query='SELECT COUNT(*) AS TOTAL from megaleiloes where codigoImovel = %s' 		
	cursor =  getCursor()
	cursor.execute(query,(chave,))	
	rs = cursor.fetchall()
	if int(rs[0][0]) == 0:
		return False
	else:
		return True

def inserirNoBanco(dadosImovel):	
	#TODO FAZER AS QUERYS
	cursor = getCursor()
	if(existeRegistro(dadosImovel['codigoImovel'])):		
		print('Update')
		#query = 'UPDATE megaleiloes SET titulo = %s,categoria = %s,subcategoria = %s,status = %s,praca = %s,tipo = %s,leilao = %s,lance_inicial = %s,ultimo_lance = %s,incremento = %s,localizacao = %s,inicio = %s,termino = %s,endereco = %s,comitente = %s,vara = %s,forum = %s,num_processo = %s,link_processo = %s,controle_num = %s,autor = %s,reu = %s,descricao = %s,valor_avaliacao = %s,edital = %s,laudo_avaliacao = %s,matricula = %s,mapa = %s,imagens = %s WHERE codigoImovel = %s;'
	else:
		print('Insert')
		#query = 'INSERT INTO megaleiloes (codigoImovel, titulo, categoria, subcategoria, status, praca, tipo, leilao, lance_inicial, ultimo_lance, incremento, localizacao, inicio, termino, endereco, comitente, vara, forum, num_processo, link_processo, controle_num, autor, reu, descricao, valor_avaliacao, edital, laudo_avaliacao, matricula, mapa, imagens) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'		
	
	#cursor.execute(query, (tituloImovel, categoria, subcategoria, statusImovel, pracaImovel, tipoImovel, leilaoImovel, lanceinicialImovel, ultimolanceImovel, incrementoImovel, localizacaoImovel, inicioImovel, terminoImovel, enderecoImovel, comitenteImovel, varaImovel, forumImovel, numprocessoImovel, linkprocessoImovel, controlenumImovel, autorImovel, reuImovel, descricaoImovel.strip(), valoravaliavaoImovel, editalImovelPDF, laudoImovelPDF, matriculaImovelPDF, enderecoImovel, str(imagensparaBanco),codigoImovel))
	#connector.commit()
	#cursor.close()
	

def varrerImoveis():
	for categoria in categorias:
		url_base = "https://www.megaleiloes.com.br/imoveis/"+categoria+"?pagina="
		proximo = True
		numeroAtual  = 1
		while(proximo):
			# carregando a pagina no requests.get
			print(url_base+str(numeroAtual))
			paginaInicial = pegarconteudo(url_base+str(numeroAtual))
			soup = BeautifulSoup(paginaInicial[0], "lxml")
			# se não teve erro 404 prosseguir
			if paginaInicial[1] != '404':		
				finaldaspaginas = soup.find("li", class_="next disabled")		
				if finaldaspaginas == None:
					numeroAtual = numeroAtual + 1
					miniaturas = soup.find("ul", class_="thumbnails").find_all("li", class_="item-row")
					#TESTAR FOR
					for miniatura in miniaturas:
						linkdoImovel = miniatura.find("a", class_="card-image")['href'].replace('//','/').replace(':/','://')					
						dadosImovel = obterDados(linkdoImovel)
						inserirNoBanco(dadosImovel)
				else:
					proximo=False

varrerImoveis()