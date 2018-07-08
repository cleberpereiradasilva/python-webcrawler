class Animal:	
	#constructor
	def __init__(self, tipo):
		self.tipo = tipo		

	def __setSangue__(self, s):
		self.sangue = s #quente ou frio

	def getSangue(self):
		print(self.sangue)

	def getTipo(self):
		print(self.tipo)

class Pet(Animal):	
	#constructor	
	def __init__(self, nome, qtdPatas, somEleEmite):				
		Animal.__init__(self,'Mamifero')
		Animal.__setSangue__(self,'quente')				
		self.patas = qtdPatas
		self.som = somEleEmite
		self.name = nome

	def getName():
		print(self.name)
	
	def getPatas(self):
		print(self.patas)	

	def emitirSom(self):
		print(self.som)

class Cao(Pet):	
	def __init__(self, nome):				
		Pet.__init__(self, nome, 4,'auau')

class Gato(Pet):			
	def __init__(self, nome):		
		Pet.__init__(self, nome , 4,'meaw')



Marie = Gato('Marie')
Marie.emitirSom()






