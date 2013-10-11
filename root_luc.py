#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright © 2013, W. van Ham, Radboud University Nijmegen
Copyright © 2013, I. Clemens, Radboud University Nijmegen,for the Kontsevich class
This file is part of Sleelab.

Sleelab is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Sleelab is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Sleelab.  If not, see <http://www.gnu.org/licenses/>.

The functions and functors in the module can be used in Sleelab experiment
files. 
'''

from __future__ import print_function
import math, numpy as np, re, random
import time, threading

class Bisect():
	"""root finding functor, determine what x-value to probe next"""
	def __init__(self, min, max):
		self.min = min
		self.max = max
		self.x = 0.5*(min+max)
		
	def __call__(self):
		return self.x
		
	def down(self):
		self.max = self.x
		self.x = 0.5*(self.min+self.max)

	def up(self):
		self.min = self.x
		self.x = 0.5*(self.min+self.max)
		
	def addMeasurement(self, m):
		if m:
			self.down()
		else:
			self.up()

		
class Random():
	"""Return random values betwen min and max."""
	def __init__(self, min, max):
		self.min = min
		self.max = max
		
	def __call__(self):
		return self.min + (self.max-self.min)*random.random()
		
	def down(self):
		pass

	def up(self):
		pass
	
	def addMeasurement(self, m):
		if m:
			self.down()
		else:
			self.up()

class Step():
	"""non converging root finding functor"""
	nValue=10
	def __init__(self, min, max):
		self.values = np.linspace(min, max, self.nValue)
		self.iValue = self.nValue//2
		
	def __call__(self):
		return self.values[self.iValue]
		
	def down(self):
		if self.iValue > 0:
			self.iValue -= 1

	def up(self):
		if self.iValue < self.nValue-1:
			self.iValue += 1
			
	def addMeasurement(self, m):
		if m:
			self.down()
		else:
			self.up()
			
from scipy.stats import norm
class Psi:
	"""Implements Kontsevich adaptive estimation of psychometric slope and threshold. """
	def __init__(self, xMin=None, xMax=None, x=None, mu = None, sigma = np.linspace(0.1, 10, 21), lapseRate = 0.04):
		"""Setup adaptive psychometric procedure
		
		Keyword arguments:
		options -- dictionary with settings, the following keys are supported:
			- x -- Possible stimuli
			- mu -- Sampling points for mu in p(mu, sigma)
			- sigma -- Sampling points for sigma in p(mu, sigma)
		"""
		
		# possible stimulus values
		if x != None:
			self.x = x
		elif xMin != None and xMax != None:
			self.x = np.linspace(xMin, xMax, 101)
		else:
			self.x = np.linspace(0, 30, 81)

		# values of mu for which we compute p(mu, sigma | responses)
		if mu == None:
			self.mu = self.x
		else:
			self.mu = mu
			
		#print ("x : {}", self.x)
		#print ("mu: {}", self.mu)
		
		# values of sigma for which we compute p(mu, sigma | responses)
		self.sigma = sigma
		
		
		# number of responses on this x stimules
		self.hist = np.zeros(np.shape(self.x), dtype="int")  
		
		# number of True responses for this x stimulus
		self.y = np.zeros(np.shape(self.x), dtype="int")     

		# assumed lapse rate lambda (equals guess rate)
		self.lapseRate = lapseRate
		
		self.nMu = len(self.mu)
		self.nSigma = len(self.sigma)
		self.nx = len(self.x)

		# Number of theta values (all combinations of mu and simga)
		self.nTheta = self.nMu * self.nSigma

		"""Initialize lookup tables to speed up computation during experiment"""
		self.lookup = np.zeros((self.nx, self.nTheta))
				
		for i in range(0, self.nTheta):
			self.lookup[:, i] = self.lapseRate + \
				(1 - 2 * self.lapseRate) * norm.cdf(self.x, self.mu[i / self.nSigma], self.sigma[i % self.nSigma])

		# Reset p(mu, sigma) of curve to prior
		self.pTheta = np.ones(self.nTheta) / self.nTheta
		
		self.calcNextStim()
		
	def up(self):
		self.addMeasurement(False)

	def down(self):
		self.addMeasurement(True)
		
	def addMeasurement(self, response, stimulus=None):
		"""Updates p(mu, sigma) of curve given new data"""
	 
		if stimulus == None:
		 stimulus = self.stim
		self.stim = None # this remains None until calcNextStim has finished in the background
		
		# Find nearest stimulus
		ix = np.argmin(abs(self.x - stimulus))
		prx = self.lookup[ix, 0:self.nTheta] # probability of this x
		
		# Update probability depending on response
		self.hist[ix] += 1
		if(response == False):
			self.pTheta *= (1 - prx)
		else:
			self.y[ix] += 1
			self.pTheta *= prx

		# Normalize
		self.pTheta /= sum(self.pTheta)
		# schedule calculation
		#self.calcNextStim()
		threading.Thread(target = self.calcNextStim).start()
		return self.pTheta
		
	def getData(self):
		""" return x, y, number of occurences (the way psignifit likes the data) """
		iNotNan = self.hist != 0
		return np.c_[self.x[iNotNan], 1.0*self.y[iNotNan]/self.hist[iNotNan], self.hist[iNotNan]]
		
	def getXY(self):
		return self.x, self.y

	def getTheta(self):
		#i,j =np.unravel_index(np.argmax(self.pTheta),self.pTheta.shape)
		i = np.argmax(self.pTheta)
		SIGMA,MU = np.meshgrid(self.sigma,self.mu)
		MU = MU.flatten()
		SIGMA = SIGMA.flatten()
		mu_opt = MU[i]
		sigma_opt = SIGMA[i]
		return mu_opt, sigma_opt

	def __call__(self):
		while(self.stim==None):
			time.sleep(.1)
		return self.stim
		
	def calcNextStim(self):
		"""Finds best stimulus to present next, usually runs in the background."""
		H = np.zeros(self.nx)
				
		for x in range(0, self.nx):
			pttrx_l = self.pTheta * (1 - self.lookup[x, 0:self.nTheta])
			pttrx_r = self.pTheta * (self.lookup[x, 0:self.nTheta])
			
			ptrx_l = sum(pttrx_l)
			ptrx_r = sum(pttrx_r)

			pttrx_l = pttrx_l / ptrx_l
			pttrx_r = pttrx_r / ptrx_r
			
			H_l = -sum(pttrx_l * np.log(pttrx_l + 1e-10))
			H_r = -sum(pttrx_r * np.log(pttrx_r + 1e-10))
			
			H[x] = ptrx_l * H_l + ptrx_r * H_r

		self.stim = self.x[np.argmin(H)]

	

def test(x):
	return x*x-2
	
if __name__ == '__main__':
	# attempt to find root if test function with root finder on command line 
	# the root is at sqrt(2).
	import sys
	
	# get minimizer
	thisModule = sys.modules[__name__]
	
	# read alternative function from command line
	if len(sys.argv) > 1:
		m = re.match('(\w+)\(([\d\-\+\.Ee]+)\,\s*([\d\-\+\.Ee]+)\)', sys.argv[1])
		if m:
			functionString = m.group(1)
			min = float(m.group(2))
			max = float(m.group(3))
			init = getattr(thisModule, functionString)
			minimizer = init(min, max)
		else:
			functionString = sys.argv[1]
			init = getattr(thisModule, functionString)
			minimizer = init(0, 2)
	else:
		minimizer = Psi(0,2)
	print("using: {}".format(minimizer))
	
	# loop
	for i in range(10):
		t = time.time()
		x = minimizer()
		dt = time.time()-t
		if test(x) < 0:
			print("x: {} ↑".format(minimizer()))
			minimizer.up()
		else:
			print("x: {} ↓".format(minimizer()))
			minimizer.down()
		print ("  get: {:6.3f} ms, set: {:6.3f} ms".format(1000*dt, 1000*(time.time()-t-dt)))
		time.sleep(1) # without this sleep "x = minimizer()" (get) will be slow
