from random import uniform
import math
import pickle
import xml.etree.ElementTree as ET
from os import listdir
from helper import Helper
import parameters
	
#------------------------------------------ Hidden Layer ------------------------------------
	
class HiddenLayer:

	def __init__(self, node, nodeNumber, helperObject):
		
		self.nodeNumber = node
		self.numberOfInputs = nodeNumber
		self.weights = [0.0] * nodeNumber
		self.output = 0.0
		self.delta = 0.0
		self.previousDeltaWeight = [0.0] * nodeNumber
		
		# random weights between the hidden nodes and the input nodes
		for i in range(self.numberOfInputs):
			self.weights[i] = uniform(-0.05, 0.05)
		
		self.helperObject = helperObject

	
	def calculateOutput(self, inputs):
		
		net = 0.0
		for i in range(self.numberOfInputs):
			net += (inputs[i] * self.weights[i])
		
		self.output = self.helperObject.activationFunction(net)


	
	def calculateError(self, outputNodes):
		
		temp = 0.0
		for obj in outputNodes:
			temp += (obj.delta * obj.weights[self.nodeNumber])
		self.delta = self.output * (1 - self.output) * temp



	def updateWeights(self, inputs):
		
		deltaWeights = []
		for i in range(self.numberOfInputs):
			deltaWeights.append(parameters.learningRate * self.delta * inputs[i])
		
		for i in range(self.numberOfInputs):
			deltaWeights[i] += parameters.momentumValue * self.previousDeltaWeight[i]
			self.previousDeltaWeight[i] = deltaWeights[i]
			self.weights[i] += deltaWeights[i]


#------------------------------------------ Output Layer ------------------------------------

class OutputLayer:

	def __init__(self, node, nodeNumber, helperObject):
		
		self.nodeNumber = node
		self.numberOfHidden = nodeNumber
		self.weights = [0.0] * nodeNumber
		self.output = 0.0
		self.delta = 0.0
		self.previousDeltaWeight = [0.0] * nodeNumber
		
		# random weights between the hidden nodes and the output nodes
		for i in range(self.numberOfHidden):
			self.weights[i] = uniform(-0.05, 0.05)
		
		self.helperObject = helperObject


	def calculateOutput(self, inputs):
		
		net = 0.0
		for i in range(self.numberOfHidden):
			net += (inputs[i].output * self.weights[i])
		self.output = self.helperObject.activationFunction(net)
	


	def calculateError(self, expectedOutput):
		
		self.delta = self.output * (1 - self.output) * (expectedOutput - self.output)



	def updateWeights(self, hiddenNodes):
		
		deltaWeights = []
		for i in range(self.numberOfHidden):
			deltaWeights.append(parameters.learningRate * self.delta * hiddenNodes[i].output)
		
		for i in range(self.numberOfHidden):
			deltaWeights[i] += parameters.momentumValue * self.previousDeltaWeight[i]
			self.previousDeltaWeight[i] = deltaWeights[i]
			self.weights[i] += deltaWeights[i]


#------------------------------------------ Artificial Neural Network ------------------------------------

class AnnStructure:
	
	def __init__(self):
		
		self.helperObject = Helper()
		
		self.minimumValueOutput = float('inf')
		self.maximumValueOutput = float('-inf')
		
		self.normalizeMinRange = -1.0
		self.normalizeMaxRange = 1.0
		
		self.outputNodes = []
		for nodeNumber in range(parameters.numberOfOutput):
			outputNode = OutputLayer(nodeNumber, parameters.numberOfHidden, self.helperObject)
			self.outputNodes.append(outputNode)
		
		self.hiddenNodes = []
		for nodeNumber in range(parameters.numberOfHidden):
			hiddenNode = HiddenLayer(nodeNumber, parameters.numberOfInput, self.helperObject)
			self.hiddenNodes.append(hiddenNode)


class AnnTrain(AnnStructure):
	
	def __init__(self):
		
		AnnStructure.__init__(self)
		
		self.dataSet = []
		self.annResultObject = AnnValue()
		
		self.error = float('inf') # error in the network according to validation set
		self.minimumErrorWeights = None # save the minimum error weights
		self.iteration = 0  # number of iterations done
		self.minimumIterationNumber = 0 # last time when the weights gave minimum error
	
	
	
	def prepareTrainingData(self, annPath):
		
		# prepares the ann data for training
		
		annFilesNames = listdir(annPath)
		
		dataValues = []
		positiveValue = 1.0
		negativeValue = -1.0
		neutralValue = 0.0
		
		for fileName in annFilesNames:
			tree = ET.parse(annPath + '/' + fileName)	
			root = tree.getroot()
			inputs = []
			outputs = []
			dataList = []
			
			bse = []
			xchng = []
			oil = []
			gold = []
			
			for b in root.iter('bse'):
				bse.append(float(b.text))
			bse.append(float(root[3].text))
			
			for x in root.iter('exchange'):
				xchng.append(float(x.text))
			
			for o in root.iter('oil'):
				oil.append(float(o.text))
			
			for g in root.iter('gold'):
				gold.append(float(g.text))
			
			inputs.append(bse[1] - bse[0])
			inputs.append(xchng[1] - xchng[0])
			inputs.append(oil[1] - oil[0])
			inputs.append(gold[1] - gold[0])
			
			if root[2].text == 'positive':
				inputs.append(positiveValue)
			
			elif root[2].text == 'negative':
				inputs.append(negativeValue)
			
			elif root[2].text == 'neutral':
				inputs.append(neutralValue)
			
			outputs.append(bse[2] - bse[1])
			
			dataList.append(inputs)
			dataList.append(outputs)
			
			dataValues.append(dataList)
		
		inputLength = len(dataValues[0][0])
		outputLength = len(dataValues[0][1])
		dataSetLength = len(dataValues)
		
		# normalize the inputs in dataValues
		
		# mean of all values	
		meanInputs = [sum([data[0][i] for data in dataValues]) for i in range(inputLength)]
		meanInputs = [(m / (dataSetLength * 1.0)) for m in meanInputs]
		
		# standard deviation of all values
		standardDeviationInputs = [sum([(data[0][i] - meanInputs[i]) ** 2 for data in dataValues]) for i in range(inputLength)]
		standardDeviationInputs = [math.sqrt(val / (dataSetLength * 1.0)) for val in standardDeviationInputs]
		
		# z-score normalization of the data values
		dataValues = [[[self.helperObject.zscoreNormalize(data[0][i], meanInputs[i], standardDeviationInputs[i]) for i in range(inputLength)], data[1]] for data in dataValues]
		
		if parameters.functionType == 1:
			self.normalizeMinRange = 0.0
		else:
			pass
		
		# normalize the outputs in dataValues
		i = 0
		maxValueInput = []
		minValueInput = []
		while i < outputLength:
			maxValueInput.append(max(dataValues, key = lambda x : x[1][i])[1][i])
			minValueInput.append(min(dataValues, key = lambda x : x[1][i])[1][i])
			i += 1
		
		dataValues = [[val[0], [self.helperObject.minMaxNormalization(val[1][0], maxValueInput[0], minValueInput[0], self.normalizeMaxRange, self.normalizeMinRange)]] for val in dataValues]
		
		self.normalizeMaxRange = maxValueInput[0]
		self.normalizeMinRange = minValueInput[0]
		
		self.dataSet = list(dataValues)
	
	
	def trainTheAnn(self):
		
		split = int(len(self.dataSet) * parameters.trainingPercent)
		trainingData = self.dataSet[:split]
		
		fileWriter = open('data/myAnn/error_graph_ann.csv', 'w')
		fileWriter.write('iteration,error\n')
		fileWriter.close()
		
		while True:
			
			self.iteration += 1
			
			# use the validation set for terminating condition
			if self.validatePhase() == True:
				break
				
			for data in trainingData:
				inputs = data[0]
				output = data[1]
				
				# calculate outputs at all nodes
				for obj in self.hiddenNodes: 
					obj.calculateOutput(inputs)
				
				for obj in self.outputNodes:
					obj.calculateOutput(self.hiddenNodes)
				
				# calculate error at output nodes
				i = 0
				for obj in self.outputNodes:
					obj.calculateError(output[i])
					i += 1
			
				# calculate error at hidden nodes
				for obj in self.hiddenNodes:
					obj.calculateError(self.outputNodes)
				
				# update weights between hidden and output layer
				for obj in self.outputNodes:
					obj.updateWeights(self.hiddenNodes)
				
				# update weights between hidden and input nodes
				for obj in self.hiddenNodes:
					obj.updateWeights(inputs)
		
		# saving the minimum error weights		
		fileWriter = open('data/myAnn/min_error_weights.pkl' , 'w')
		pickle.dump(self.minimumValueOutput, fileWriter)
		pickle.dump(self.maximumValueOutput, fileWriter)
		pickle.dump(self.normalizeMinRange, fileWriter)
		pickle.dump(self.normalizeMaxRange, fileWriter)
		pickle.dump(self.minimumErrorWeights, fileWriter)
		fileWriter.close()
		
		print "\n..Training phase completed after", self.iteration, "iterations"
		print "..Final Error perceived on Validation Set :", self.error


	def validatePhase(self):
		
		split = int(len(self.dataSet) * parameters.trainingPercent)
		validateData = self.dataSet[split :]
		
		terminate = False
		errors = []
		
		for data in validateData:
			inputs = data[0]
			output = data[1]
			
			outputReceived = self.annResultObject.getAnnResult(inputs, self)
			
			#output[0] = self.helperObject.minMaxNormalization(output[0], self.normalizeMaxRange, self.normalizeMinRange, self.maximumValueRange, self.minimumValueRange)
			#print output[0], outputReceived[0]
			
			#a = raw_input('a = ')
			
			self.minimumValueOutput = min([outputReceived[0], self.minimumValueOutput])
			self.maximumValueOutput = max([outputReceived[0], self.maximumValueOutput])
			
			error = (output[0] - outputReceived[0]) ** 2
			
			errors.append(error)
		
		averageError = sum(errors) / 2.0
		averageError = round(averageError, parameters.digitsOfSignificance)
		
		# check whether this is minimum error till now
		if averageError < self.error:
			
			fileWriter = open('data/myAnn/error_graph_ann.csv', 'a')
			fileWriter.write(str(self.iteration) + ',' + str(averageError) + '\n')
			fileWriter.close()
			
			self.error = averageError
			self.minimumIterationNumber = self.iteration
			
			# get the weights for the layers
			weights = [[] , []]
			
			for node in self.hiddenNodes: 
				for w in node.weights:
					weights[0].append(w)
			
			for node in self.outputNodes:
				for w in node.weights:
					weights[1].append(w)
			
			self.minimumErrorWeights = list(weights)
			
			print "\n..Minimum error found in iteration :", self.iteration
			print "..Current error :", self.error
		
		# 1000 iterations given to find another minimum
		else:
			if self.iteration > (self.minimumIterationNumber + 1000):
				terminate = True
			else:
				pass
		
		return terminate


class AnnValue(AnnStructure):
	
	def __init__(self):
		
		AnnStructure.__init__(self)
	
	
	def loadAnnWeights(self):
		
		fileReader = open('data/myAnn/min_error_weights.pkl', 'r')
		
		self.minimumValueOutput = pickle.load(fileReader)
		self.maximumValueOutput = pickle.load(fileReader)
		
		self.normalizeMinRange = pickle.load(fileReader)
		self.normalizeMaxRange = pickle.load(fileReader)
		
		nodeWeights = pickle.load(fileReader)
		fileReader.close()
		
		i = 0
		for node in self.hiddenNodes:
			j = 0
			while j < parameters.numberOfInput:
				node.weights[j] = nodeWeights[0][i]
				i += 1
				j += 1
		
		i = 0
		for node in self.outputNodes:
			j = 0
			while j < parameters.numberOfHidden:
				node.weights[j] = nodeWeights[1][i]
				i += 1
				j += 1
	
	
	def getAnnResult(self, inputs, annObject = None):
		
		valuesHidden = [0.0] * parameters.numberOfHidden
		outputValue = [0.0] * parameters.numberOfOutput
		
		if annObject == None:
			annObject = self
		else:
			pass
		
		j = 0
		for node in annObject.hiddenNodes:
			i = 0
			for valueInput in inputs:
				valuesHidden[j] += (valueInput * node.weights[i])
				i += 1
			valuesHidden[j] = self.helperObject.activationFunction(valuesHidden[j])
			j += 1
		
		j = 0
		for node in annObject.outputNodes:
			i = 0
			for value in valuesHidden:
				outputValue[j] += (value * node.weights[i])
				i += 1
			outputValue[j] = self.helperObject.activationFunction(outputValue[j])
			j += 1
		
		if annObject == None:
			outputValue = [self.helperObject.minMaxNormalization(value, annObject.maximumValueOutput, annObject.minimumValueOutput, annObject.normalizeMaxRange, annObject.normalizeMinRange) for value in outputValue]
		else:
			pass
		
		
		return outputValue