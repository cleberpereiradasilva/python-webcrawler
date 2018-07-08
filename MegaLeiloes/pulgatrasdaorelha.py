# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from  more_itertools import unique_everseen
import requests, sys, os, errno, mysql.connector, datetime, time, collections
from libs.funcoes import dataehora, pegarconteudo, mkdir_p, baixarimagem, baixarPDF, procurarOutrosLotes
reload(sys)
sys.setdefaultencoding('utf8')

# dados da base que vamos alimentar

db_usuario = "python"
db_senha = "contem1kg"
db_host = "127.0.0.1"
db_nomebase = "python2"

inicioExecucaoScript = datetime.datetime.now()


# começando, pegando a página principal de imóveis (somente com filtro de imoveis) e colocando ela em uma lista na 
# primeira posição

paginas = ["https://www.megaleiloes.com.br/imoveis?type=1"]

# criando um set para popular com as URLs individuais de cada imóvel

linksdosImoveis = set()

# criando um set para codigos que já foram scrapeados

codigosScrapeados = set()

# vamos ciclar pela lista pagina que sera incrementada com novas paginas a medida que o bsoup for achando mais links 
# com "próxima pagina", quando ele não encontrar mais novas páginas ele vai breakar e já vamos ter coletado todos os links
# de todos os imóveis

contador_erro_404=0

for pagina in paginas:

    # carregando a pagina no requests.get

    paginaInicial = pegarconteudo(pagina)

    # se não teve erro 404 prosseguir

    if paginaInicial[1] != '404':


        # carregando a pagina no soup

        soup = BeautifulSoup(paginaInicial[0], "lxml")



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
    elif paginaInicial[1] == '404':

        contador_erro_404 = contador_erro_404 + 1
        print ("Url: %s falhou. Erros até agora: %s" %(pagina, contador_erro_404))


    if finaldaspaginas != None:
        break


# definindo o diretório principal

diretorioArquivosImoveis = "imoveis2/"

# transformando o set linksdosImoveis criado anteriormente para lista para poder selecionar posicoes dentro dele:

linksdosImoveis = list(linksdosImoveis) 

print (type(linksdosImoveis))

# Fazendo um set para colocar o código de todos os imoveis que ja foram scrapeados

linksdeLotes = set()

codigosLotes = set()

# iniciando loop para coletar os dados dos imoveis

contadorFor = 0

paginascomLotes = []

for paginadeimovel in linksdosImoveis:

    contadorFor = contadorFor + 1

    print ("")

    print ("Total de itens linksdosImoveis: "),

    print (len(linksdosImoveis))

    print ("Quantidade de itens percorridos neste for: "),

    print (contadorFor)

    print ("Quantidade de lotes adicionais de imoveis encontrados: %s" %(len(codigosLotes)))

    # pegando o código do imóvel baseado na URL, pegando os ultimos 6 digitos

    codigoImovel = paginadeimovel.split("?")[0][-6:]

    print ("")

    print(codigoImovel)

    print ("")

    # começa carregando a pagina do imóvel no requests.get 

    print (paginadeimovel)

    requestsPaginadoImovel = pegarconteudo(paginadeimovel)

    # carregando o requests.get da pagina do imovel no bsoup

    soup = BeautifulSoup(requestsPaginadoImovel[0], "lxml")

    if requestsPaginadoImovel[1] != '404':

        partecomLotes = soup.find("div", id="batches-list")

        if partecomLotes != None:

            print ("Pagina %s tem lotes adicionais." %(paginadeimovel))

            ultimapaginadeimoveis = soup.find("div", id="batches-list").find("li",class_="next disabled")

            # se existe o botão de proximo na pagina: 

            if ultimapaginadeimoveis == None:
                
                # Vamos pegar todas as ?paginas= desse imovel

                # pegar o link de próximo e colocar em uma lista chamada paginascomLotes

                # antes vamos verificar se a parte com imoveis nao tem paginação, se nao tiver, só escanear por
                # lotes adicionais nesta URL e em nenhuma outra

                paginadeImoveiscomLoteSemPag = soup.find("div", id="batches-list").find("li",class_="next")

                if paginadeImoveiscomLoteSemPag == None:
                    paginascomLotes.append(paginadeimovel)
                else: 

                    proximaPaginadeImoveis = soup.find("div", id="batches-list").find("li",class_="next").find("a")["href"]
                    proximaPaginadeImoveis = "https://www.megaleiloes.com.br" + proximaPaginadeImoveis

                    paginascomLotes.append(paginadeimovel)
                    paginascomLotes.append(proximaPaginadeImoveis)

            # rodar um for em paginascomLotes

            for paginacomLote in paginascomLotes:

                requestspaginacomLote = pegarconteudo(paginacomLote)
                soup2 = BeautifulSoup(requestspaginacomLote[0], "lxml")

                temMaisImoveis = soup2.find("div", id="batches-list")

                if temMaisImoveis != None:
                
                    


                    # coletar os links dos lotes e colocar no set linksdeLotes

                    # transformar os links em codigo e adicionar ao set codigosLotes

                    auxOutrosLotes = soup2.find("div", id="batches-list").find("ul", class_="thumbnails").find_all("a", class_="card-header")

                    print ("Encontrados: %s lotes" %(len(auxOutrosLotes)))

                    contadorLotesDentroPagina = 0

                    for lote in auxOutrosLotes:

                        contadorLotesDentroPagina = contadorLotesDentroPagina + 1
                        linksdeLotes.add("https://www.megaleiloes.com.br" + lote["href"])
                        codigoLote = lote["href"].split("?")[0][-6:]
                        codigosLotes.add(codigoLote)
                        
                    
                    print ("%s lotes adicionados ao codigosLotes achados na %s." %(contadorLotesDentroPagina,paginacomLote))
                    print ("Tamanho da codigosLotes: %s" %(len(codigosLotes)))    

                    # pegar o li indicando que não há mais link de próximo na pagina do imovel

                    ultimoproximoImoveisLotes = soup2.find("div", id="batches-list").find("li",class_="next disabled")

                    # Se o botão de próxima página com mais lotes não existe:

                    if ultimoproximoImoveisLotes == None:

                        # pegar o link de próximo e colocar na lista paginascomLotes
                        areaDePaginacaoImoveis = soup2.find("div", id="batches-list").find("li",class_="next")
                        
                        # Se a area de paginacao com mais lotes existe:

                        if areaDePaginacaoImoveis != None:
                            proximaPaginadeImoveis = soup2.find("div", id="batches-list").find("li",class_="next").find("a")["href"]
                            proximaPaginadeImoveis = "https://www.megaleiloes.com.br" + proximaPaginadeImoveis
                            
                            if proximaPaginadeImoveis not in paginascomLotes:
                                paginascomLotes.append(proximaPaginadeImoveis)



                    #else:
                        #break
            print (paginascomLotes)            
            # Vamos zerar a lista paginacomLotes para a próxima rodada do for
            paginascomLotes = []
       
        # Coletar dados do imovel

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
            nomedoarquivoEditalPDF = editalImovelPDF.split("/")[6]
        except:
            pass

        

        try:
            laudoImovelPDF = soup.find("div", id="buttons").find_all("a")[3]["href"]
            nomedoarquivoLaudoPDF = laudoImovelPDF.split("/")[6]
        except:
            pass


        try:
            matriculaImovelPDF = soup.find("div", id="buttons").find_all("a")[4]["href"]
            nomedoarquivoMatriculaPDF = matriculaImovelPDF.split("/")[6]
        except:
            pass            

        contratoImovel = soup.find("textarea", id="contract").text

        localimagemImovel = soup.find("div", class_="span7").find("div", class_="carousel slide")

        forumImovel = "N/D"
        varaImovel = "ND"
        forumImovel = "ND"
        varaImovel = "ND"
        numprocessoImovel = "ND"
        controlenumImovel = "ND"
        linkprocessoImovel = "ND"
        autorImovel = "ND"
        reuImovel = "ND"
        valoravaliavaoImovel = "ND"


        if tipoImovel == "Leilão Judicial":
            forumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[2].find("td").text
            varaImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[1].find("td").text
            numprocessoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").find("a").text
            controlenumImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].find("td").text[-8:]
            linkprocessoImovel = soup.find("div", class_="span9").find("a")["href"]
            autorImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[4].find("td").text
            reuImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[5].find("td").text
            valoravaliavaoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[7].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()
          


        comitenteImovel = "N/D"            

        if tipoImovel == "Leilão Extrajudicial":
            comitenteImovel = soup.find("div", class_="span9").find_all("tr")[1].find("td").text
            try:
                valoravaliavaoImovel = soup.find("table", class_="table table-nomargin").find_all("tr")[3].text.split("}")[1].split("A descr")[0].split("o:")[1].strip()
            except: 
                pass

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

            # eu poderia ter usado um imagemImovel.split e depois um if len(imagemImovel) < 6 abaixo, eu sei....
            try: 
                nomeFoto = imagemImovel.split("/")[6]
            except IndexError:
                nomeFoto = imagemImovel.split("/")[5]

            baixarimagem(imagemImovel,str(diretorioDasImagens) + str(nomeFoto),str(nomeFoto))
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
                baixarimagem(caminhoImagem, str(diretorioDasImagens) + str(nomeFoto),str(nomeFoto))



        # baixando os pdfs do imóvel:


        try: 
            baixarPDF(editalImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoEditalPDF),str(nomedoarquivoEditalPDF))
        except:
            pass
        try: 
            baixarPDF(laudoImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoLaudoPDF),str(nomedoarquivoLaudoPDF))
        except:
            pass
        
        if tipoImovel == "Leilão Judicial":
            baixarPDF(matriculaImovelPDF, str(diretorioDoImovel) + str(nomedoarquivoMatriculaPDF),str(nomedoarquivoMatriculaPDF))


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

        codigoImovel = paginadeimovel.split("?")[0][-6:]

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

        queryUpdateDadosBanco = 'UPDATE megaleiloes SET titulo = %s,categoria = %s,subcategoria = %s,status = %s,praca = %s,tipo = %s,leilao = %s,lance_inicial = %s,ultimo_lance = %s,incremento = %s,localizacao = %s,inicio = %s,termino = %s,endereco = %s,comitente = %s,vara = %s,forum = %s,num_processo = %s,link_processo = %s,controle_num = %s,autor = %s,reu = %s,descricao = %s,valor_avaliacao = %s,edital = %s,laudo_avaliacao = %s,matricula = %s,mapa = %s,imagens = %s WHERE codigoImovel = %s;'

        queryInserirDadosBanco = 'INSERT INTO megaleiloes (codigoImovel, titulo, categoria, subcategoria, status, praca, tipo, leilao, lance_inicial, ultimo_lance, incremento, localizacao, inicio, termino, endereco, comitente, vara, forum, num_processo, link_processo, controle_num, autor, reu, descricao, valor_avaliacao, edital, laudo_avaliacao, matricula, mapa, imagens) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'


        cursor.execute(queryUpdateDadosBanco, (tituloImovel, categoria, subcategoria, statusImovel, pracaImovel, tipoImovel, leilaoImovel, lanceinicialImovel, ultimolanceImovel, incrementoImovel, localizacaoImovel, inicioImovel, terminoImovel, enderecoImovel, comitenteImovel, varaImovel, forumImovel, numprocessoImovel, linkprocessoImovel, controlenumImovel, autorImovel, reuImovel, descricaoImovel.strip(), valoravaliavaoImovel, editalImovelPDF, laudoImovelPDF, matriculaImovelPDF, enderecoImovel, str(imagensparaBanco),codigoImovel))

        connector.commit()




        # 'INSERT INTO megaleiloes (titulo, categoria, subcategoria, status, praca, tipo, leilao, lance_inicial, ultimo_lance, incremento, localizacao, inicio, termino, endereco, comitente, vara, forum, num_processo, link_processo, controle_num, autor, reu, descricao, valor_avaliacao, edital, laudo_avaliacao, matricula, mapa, imagens) VALUES (' + str(tituloImovel.strip()) + ', ' +  categoria + ', ' + subcategoria + ', ' + statusImovel + ', ' + pracaImovel + ', ' + tipoImovel + ', ' + leilaoImovel + ', ' + lanceinicialImovel + ', ' + ultimolanceImovel + ', ' + incrementoImovel + ', ' + localizacaoImovel + ', ' + inicioImovel + ', ' + terminoImovel + ', ' + enderecoImovel + ', ' + comitenteImovel + ', ' + varaImovel + ', ' + forumImovel + ', ' + numprocessoImovel + ', ' + linkprocessoImovel + ', ' + controlenumImovel + ', ' + autorImovel + ', ' + reuImovel + ', ' + descricaoImovel.strip() + ', ' + valoravaliavaoImovel + ', ' + editalImovelPDF + ', ' + laudoImovelPDF + ', ' + matriculaImovelPDF + ', ' + enderecoImovel + ', ' + str(imagensparaBanco) + ');'    

        rowsaffected = cursor.rowcount

        if rowsaffected == 0:

            cursor.execute(queryInserirDadosBanco, (codigoImovel, tituloImovel, categoria, subcategoria, statusImovel, pracaImovel, tipoImovel, leilaoImovel, lanceinicialImovel, ultimolanceImovel, incrementoImovel, localizacaoImovel, inicioImovel, terminoImovel, enderecoImovel, comitenteImovel, varaImovel, forumImovel, numprocessoImovel, linkprocessoImovel, controlenumImovel, autorImovel, reuImovel, descricaoImovel.strip(), valoravaliavaoImovel, editalImovelPDF, laudoImovelPDF, matriculaImovelPDF, enderecoImovel, str(imagensparaBanco)))

            connector.commit()
            connector.close()
            cursor.close()

        connector.close()
        cursor.close()


        # colocar codigodoImovel em codigosScapeados

        codigosScrapeados.add(codigoImovel)


        try: 
            del tituloImovel 
            del categoria 
            del subcategoria 
            del pracaImovel 
            del tipoImovel 
            del leilaoImovel 
            del lanceinicialImovel 
            del ultimolanceImovel 
            del incrementoImovel 
            del localizacaoImovel 
            del inicioImovel 
            del terminoImovel 
            del enderecoImovel 
            del descricaoImovel 
            del editalImovelPDF 
            del nomedoarquivoEditalPDF 
            del laudoImovelPDF 
            del nomedoarquivoLaudoPDF 
            del contratoImovel 
            del localimagemImovel 
            del tipoImovel 
            del forumImovel 
            del varaImovel 
            del numprocessoImovel 
            del controlenumImovel 
            del linkprocessoImovel 
            del autorImovel 
            del reuImovel 
            del valoravaliavaoImovel 
            del matriculaImovelPDF 
            del nomedoarquivoMatriculaPDF 
            del comitenteImovel 
            del valoravaliavaoImovel 
        except:
            pass

        # evitando duplicatas
        # se o codigo estiver no set

    elif requestsPaginadoImovel[1] == '404':
        contador_erro_404 = contador_erro_404 + 1
        print ("Url: %s falhou. Erros até agora: %s" %(paginadeimovel, contador_erro_404))

listadiferenca = codigosLotes.difference(codigosScrapeados)



print ("")
#print ("Lista de imoveis percorridos:")
#print (sorted(linksdosImoveis))
print ("Concluído")
print ("Inicio: "),
print (inicioExecucaoScript)
terminoExecucaoScript = datetime.datetime.now()
print ("Término: "),
print (terminoExecucaoScript)
tempodeExecucao = (terminoExecucaoScript - inicioExecucaoScript).total_seconds()
print ("Tempo de execução: %s segundos" %(tempodeExecucao))
print ("Total de itens linksdosImoveis: "),
print (len(linksdosImoveis))
print ("Quantidade de itens percorridos no for: "),
print (contadorFor)
print ("Diferença do codigosLotes para o codigosScrapeados: %s" %listadiferenca)
print ("Tamanho da codigosLotes: %s" %len(codigosLotes))
print ("Tamanho da codigosScrapeados: %s" %len(codigosScrapeados))

