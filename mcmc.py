class STRUCT():
	def __init__(self, value = ''):
		self.value = value
	def get(self):
		return self.value
	def set(self, value):
		self.value = value			

def getmin(values):
	min = values[0]
	for value in values:
		if value < min:
			min = value
	return min	
	
def getmax(values):
	max = values[0]
	for value in values:
		if value > max:
			max = value
	return max			

class PRIOR():
	def __init__(self, priors):
		self.lower = getmin(priors)
		self.upper = getmax(priors)
					
def BoxMuller():
	from random import random
	import math
	v1 = random()
	v2 = random()
	bm = math.sqrt( - 2.0 * math.log( v1 ) ) * math.cos( 2.0 * math.pi * v2 )	
	return bm
		
def prettyPrint(v1,v2,sp, where):
	string = '{0:' + str(sp) + '}{1}'
	string = string.format(v1,v2)
	where.write(string + '\n')


class MCMC_param():

	def __init__(self, pname = 'param1', pdesc = 'description', sigma = 1.0, priors = [0,1], output = ''):
		self.pname = STRUCT(pname)
		self.pdesc = STRUCT(pdesc)
		self.sigma = STRUCT(sigma)
		self.priors = STRUCT( PRIOR(priors) )
		self.paramValue = STRUCT( self.pick() )
		self.newParamValue = STRUCT( self.paramValue.get() )
		self.output = output

	def unitRand(self):
		import random
		return random.random()
		
	def printInfo(self):
		sp = 25
		import sys
		prettyPrint('Parameter name:',self.pname.get() ,sp,sys.stdout)
		prettyPrint('Parameter description:',self.sigma.get(),sp,sys.stdout)
		prettyPrint('Prior (lower):',self.priors.get().lower,sp,sys.stdout)
		prettyPrint('Prior (upper):',self.priors.get().upper,sp,sys.stdout)
		prettyPrint('Parameter value:',self.paramValue.get(),sp,sys.stdout)			
		
	def pick(self):
		
		try:	
			while True:
				newValue = self.paramValue.get() +  BoxMuller() * self.sigma.get()
				if newValue <= self.priors.get().upper and newValue >= self.priors.get().lower:
					break			
			self.newParamValue.set( newValue )
			
		except:
			return (self.priors.get().upper  - self.priors.get().lower) * self.unitRand() + self.priors.get().lower

	def acceptNewValue(self):
	
		self.paramValue.set( self.newParamValue.get() )
	
		
	def rejectNewValue(self):
	
		self.newParamValue.set( self.paramValue.get() )
	

class MCMC():
	
	def __init__(self, params = [], data = [], theory = '', nsteps = 100, nburn = 50, stateFileName = 'state.dat'):
		self.params = params
		self.data = data		
		self.likelihood = STRUCT(1E6)
		self.nsteps = STRUCT(nsteps)
		self.nburn = STRUCT(nburn)
		self.stateFileName = stateFileName
		self.stateFile = open(self.stateFileName,'w')
		self.stateFile.close()
		self.count = 0
		self.naccept = 0
		self.nreject = 0
		
		pass
		
	def printParamInfo(self):
		for param in self.params:
			param.printInfo()
			print ''
		print ''	
		
	def get_new_values(self):
		for param in self.params:
			param.pick()	
	
	def accept(self):
		self.naccept += 1
		for param in self.params:
			param.acceptNewValue()
	
	def reject(self):
		self.nreject += 1
		for param in self.params:
			param.rejectNewValue()
	
	def calcLikelihood(self):
		import math
		predict = []
		av = 0.0
		for data in self.data:
			x = data[0]
			y = data[1]
			m = self.params[0].newParamValue.get()
			c = self.params[1].newParamValue.get()
			y_predict = m * x + c
			pre = [x, y_predict]
			predict.append(pre)
			av += ( y - y_predict ) * ( y - y_predict )
		
		av /= len(self.data)

		self.likelihood.set( math.log(av) )

			
	def dumpState(self):
		self.stateFile = open(self.stateFileName,'a')
		string = str(self.count) + ' '
		for param in self.params:
			string += str(param.paramValue.get()) + ' ' 
		string += str(self.likelihood.get())
		self.stateFile.write(string + '\n')	
		self.stateFile.close()
		
				
				
	def doMCMC(self):
		
		self.get_new_values()
		self.calcLikelihood()
		
		for x in xrange(0, self.nsteps.get()):
	
			oldL = self.likelihood.get()
			self.get_new_values()
			self.calcLikelihood()
			newL = self.likelihood.get()
			if self.count > self.nburn.get():
				if newL < oldL:
					self.accept()
					self.likelihood.set(newL)
				else:
					self.reject()
					self.likelihood.set(oldL)
				self.dumpState()			
			self.count += 1	
		
	def printFinalInfo(self):
		print ''
		print 'FINAL PARAMETER VALUES'	
		print 'Number of MCMC samples:', self.count	
		print 'Final likelihood:', self.likelihood.get()
		print 'Number of accepted samples:', self.naccept
		print 'Number of rejected samples:', self.nreject
		string = ''
		for param in self.params:
			string +=  param.pname.get() + ' ' + str(param.paramValue.get()) + '\n'
		print string	
	
	
import sys			

m = MCMC_param(pname = 'm', pdesc = 'Gradient', sigma = 0.01, priors = [0.5,1.5], output = sys.stdout)
c = MCMC_param(pname = 'c', pdesc = 'Intercept', sigma = 0.01, priors = [-0.5,0.5], output = sys.stdout)
data = [[0,0],[1,1],[2,2],[3,3]]
nsteps = 1000

params = MCMC( params = [m, c], data = data, nsteps = nsteps )
params.printParamInfo()
params.doMCMC()
params.printFinalInfo()
		
		
	                                     
		