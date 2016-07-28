from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer, SoftmaxLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from os import listdir
import pickle
import xml.etree.ElementTree as ET
import parameters

#------------------------------------------------- AnnStructure class ------------------------------------------------

class AnnStructure:
	
	def __init__(self):
		
		# the ann network
		self.net = buildNetwork(parameters.numberOfInput, parameters.numberOfHidden, parameters.numberOfOutput, bias=True, hiddenclass=TanhLayer, outclass = SoftmaxLayer)


class AnnTrain(AnnStructure):
	
	def __init__(self):
		
		# initialize the base class
		AnnStructure.__init__(self)
		
		# the supervised data set
		self.dataSet = SupervisedDataSet(parameters.no_of_inputs, parameters.no_of_output)


	def prepareTrainingData(self, annPath):
		
		# get the data in an list
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
		
		# add the data from list in the supervised data set
		for data in dataValues:
			self.dataSet.addSample(tuple(data[0]), tuple(data[1]))
	
	
	def trainTheAnn(self):
		
		# backpropagation training done
		trainer = BackpropTrainer(self.net, dataset = self.dataSet, learningrate = parameters.learningRate, momentum = parameters.momentumValue)
		trainErrors, validationErrors = trainer.trainUntilConvergence(validationProportion = 0.25, maxEpochs = parameters.maxEpochs, continueEpochs = 10)
		
		# save the train and validaton set error
		fileWriter = open('data/error_graph_ann.csv', 'w')
		fileWriter.write('Epoch,Training,Validation\n')
		
		epoch = 0
		for trainingError, validationError in zip(trainErrors, validationErrors):
			fileWriter.write(str(epoch) + ',' + str(trainingError) + ',' + str(validationError) + '\n')
			epoch += 1
		
		fileWriter.close()
		
		# saving the network trained
		fileWriter = open('data/min_error_weights.pkl', 'w')
		pickle.dump(self.net, fileWriter)
		fileWriter.close()
	
	
class AnnValue(AnnStructure):
	
	def __init__(self):
		
		# initialize the base class
		AnnStructure.__init__(self)
	
	
	def loadAnnWeights(self):
		
		# get the saved network
		fileReader = open('data/min_error_weights.pkl', 'r')
		self.net = pickle.load(fileReader)
		fileReader.close()
	
	
	def getAnnResult(self, inputs):
		
		return self.net.activate(tuple(inputs))