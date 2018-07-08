# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import datetime
import time
import sys, os, errno
import urllib


# Data e hora

def dataehora():

	print ('')
	print ("Data e hora: " + datetime.datetime.now().strftime("%d-%m-%y-%H:%M"))
	print ('')

# Pegando conteúdo

def pegarconteudo(url):
	aux = requests.get(url,headers={"content-type":"text"})
	return str(aux.content), str(aux.status_code)

# Download de conteúdo	


#todo acertar funcoes de downlaod...
def baixar(url, destino):
    try:
        r = requests.get(url)
        open(destino, 'wb').write(r.content)
        return True
    except:
        return False

def baixarimagem(url, destino, nomefoto):

	if os.path.isfile(destino) == True:
		print ("Imagem %s já existe, não vamos baixa-lo." %nomefoto)
	else:
	    try:
	        r = requests.get(url)
	        open(destino, 'wb').write(r.content)
	        return True
	    except:
	        return False        

def baixarPDF(url,destino,nomearquivo):

	if os.path.isfile(destino) == True:
		print ("Arquivo PDF %s já existe, não vamos baixa-lo." %nomearquivo)

	else:
	
		try:
			urllib.urlretrieve(url, destino)
			return True
		except:
		 	return False


# Criando diretórios recursivamente

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def procurarOutrosLotes(soup,linksdosImoveis):

# 2:55am - aqui embaixo eu tentei fazer um jeito para pegar os links dos lotes adicionais dentro de cada imovel 
# só que do jeito que eu fiz não vai dar certo porque eu to transformando a lista em set e depois de volta em lista
# e quando eu faço isso eu perco a ordem da lista obviamente e vou ficar em um loop eterno   			
#
# 8:42am - descobri essa funcao na library more_itertools do python que limpa duplicatas em uma lista visando 
# performance, chama  unique_everseen(), https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
# então ao inves de transformar a lista que eu vou somar a lista do for em set e perder a ordem aqui embaixo, eu agora 
# mantenho ela como lista e rodo o o unique_everseen() para manter os itens unicos e somo essa lista com a lista do loop
# 

	outrosLotes = []

	try:

	  	auxOutrosLotes = soup.find("div", id="batches-list-min").find_all("a")

	  	print ("-----------------")	
	  	print ("Tamanho da outrosLotes no INICIO da funcao: %s" %(len(outrosLotes))) 
	  	print ("")	  		  	
	  	print ("-----------------")
	  	print ("Tamanho da linksdosImoveis no INICIO da funcao: %s" %(len(linksdosImoveis))) 
	  	print ("")
	  	print ("Links encontrados: %s links" %(len(auxOutrosLotes))) 
	  	print ("")


	  	#print ("O tipo do auxOutrosLotes é:"),
	  	#print (type(auxOutrosLotes))
	  	#print ("O conteudo do auxOutrosLotes é:"),
	  	#print (auxOutrosLotes)	  	

	  	for lote in auxOutrosLotes:

	  		# 2:45 - problema, remover os ultimos 9 caracteres do href abaixo vai tirar o ?pagina=1 da URL
	  		# e assim não vamos acessar as outras paginas com mais botoes para clicar e por no set
	  		# se eu mandar com ?pagina=1 vamos quebrar a leitura do código na variavel codigoImovel 
	  		# - RESOLVIDO - fiz isso com a codigoImovel: codigoImovel = paginadeimovel.split("?")[0][-6:]

	  		outrosLotes.extend(["https://www.megaleiloes.com.br" + lote["href"]])


	  	# print ("Outros lotes:")

	  	# print (outrosLotes)

	  	print ("")
	  	print ("Tamanho da outrosLotes ANTES de tratada por duplicata: %s" %(len(outrosLotes)))
	  	print ("")


	  	# print ("Tipo dos outros lotes:")

	  	# print (type(outrosLotes))

	  	outrosLotes = list (unique_everseen(outrosLotes))


	  	print ("")
	  	print ("Tamanho da outrosLotes DEPOIS de tratada por duplicata: %s" %(len(outrosLotes))) 
	  	print ("")	  	
	  	
	  	# print ("")

	  	# print ("Tipo dos outros lotes depois de ficar unico:")

	  	# print (type(outrosLotes))

	  	print ("Tamanho da linksdosImoveis ANTES de receber outrosLotes: %s" %(len(linksdosImoveis))) 	  

	  	linksdosImoveis.extend(outrosLotes)

	  	print ("")
	  	print ("Adicionado outrosLotes para linksdosImoveis") 
	  	print ("Tamanho da linksdosImoveis DEPOIS de receber outrosLotes: %s" %(len(linksdosImoveis))) 	  	
	  	print ("")	  

	  	# Vamos limpar a outrosLotes depois de te-la adicionado a linksdosImoveis

	  	outrosLotes=[]

	  	linksdosImoveis = list (unique_everseen(linksdosImoveis))

	  	print ("")
	  	print ("Tamanho da linksdosImoveis DEPOIS de tratada por duplicata: %s" %(len(linksdosImoveis))) 	

	  	# print ("")

	  	# print ("linksdosImoveis extendida com Outros lotes")

	  	# print (linksdosImoveis)

	  	print ("Tamanho da outrosLotes no FINAL da funcao: %s" %(len(outrosLotes))) 
	  	print ("-----------------")	 	  	

	  	return linksdosImoveis, outrosLotes

	except:
		pass
