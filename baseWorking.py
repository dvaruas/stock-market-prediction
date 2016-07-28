from os import remove, rename, listdir
from os.path import isfile
import time
import datetime
import xml.etree.ElementTree as ET
from shutil import copy
from featuresGet import GetFeatures
from svmClassifier import SVMResult, SVMTrain
from tradingEngine import TradingEngine
from helper import Helper
import parameters

#-------------------------------------------------------------------------------------------------------------------------

class HagneauImplementation:
	
	def __init__(self):
		
		self.featuresObject = GetFeatures('corpora')
		self.helperObject = Helper()
		self.svmObject = None
	

	def extractFeatures(self):
		
		if isfile('data/all_features.pkl'):
			remove('data/all_features.pkl')
		else:
			pass
		
		self.helperObject.corpusFilesLoader(True)
		
		extractionTimeStart = time.time()
		self.featuresObject.extractFeatures(parameters.baseFeatureType)
		extractionTimeEnd = time.time()
		
		print 'Features Extraction Time : %.2f minutes' %((extractionTimeEnd - extractionTimeStart) / 60)
	
	
	def selectFeatures(self):
		
		selectionTimeStart = time.time()
		self.featuresObject.selectFeatures(parameters.baseSelectionType, parameters.numberOfFeatures)
		selectionTimeEnd = time.time()
		
		print 'Features Selection Time : %.2f minutes' %((selectionTimeEnd - selectionTimeStart) / 60)
	
	
	def getVectors(self):
		
		representationTimeStart = time.time()
		numberOfVectorsFormed = self.featuresObject.representFeatures()
		representationTimeEnd = time.time()
		
		numberForTraining = int(numberOfVectorsFormed * parameters.percentageTrainVectors)
		
		print 'Document Vectors representation time : %.2f minutes' %((representationTimeEnd - representationTimeStart) / 60)
	
	
	def trainSVM(self):
		
		self.svmObject = SVMTrain(True)
		self.svmObject.prepareSVM()
		self.svmObject.trainingPhase()
	
	
	def classifyResults(self):
		
		self.svmObject = SVMResult(True)
		self.svmObject.prepareSVM()
		
		result = self.svmObject.svmObject.cv(self.svmObject.trainData, numFolds = 5)
		
		print 'Classification accuracy : ', result.getBalancedSuccessRate()

	
	def doTrading(self):
		
		self.svmObject = SVMResult(True)
		self.svmObject.prepareSVM()
		
		choice = 'y'
		while choice != 'n':
			
			enteredDate = raw_input('Enter date (dd-mm-yyyy): ')
			dayList = enteredDate.split('-')
			dayList = [int(i) for i in dayList]
			
			tradingDay = datetime.date(dayList[2], dayList[1], dayList[0])
			sentimentList = []
			
			dataSetPath = 'dataset/' + tradingDay.strftime('%d-%h-%G')
			
			timeNow = datetime.datetime.combine(tradingDay, datetime.time(9,15))
			endingTime = datetime.datetime.combine(tradingDay, datetime.time(15,15))
			streamTime = 0
			currentSentiment = 0.0
			totalSuccessRate = 0.0
			
			startTime = time.time()
			
			while True:
				
				fileNames = listdir('new_news')
				for fileName in fileNames:
					remove('new_news/' + fileName)
				
				print '\nTime :', timeNow.strftime('%H:%M'), '\n'
				noNewsFile = False
				
				# get the file name which is the current news
				fileReader = open(dataSetPath + '/log_file.txt', 'r')
				
				for lineNumber, line in enumerate(fileReader):
					if lineNumber == streamTime:
						newsFileName = line
					else:
						pass
				
				fileReader.close()
				
				# check whether news file is present or not
				tempValue = newsFileName.split(' ')[:-1]
				
				if tempValue[1] != '0':
					newsFileName = tempValue[0]
					
					tree = ET.parse(dataSetPath + '/corpora/' + newsFileName)
					root = tree.getroot()
					
					for sentimentNode in root.iter('sentiment'):
					
						if sentimentNode.text == 'neutral':
						    sentimentNode.text = 'positive'
						else:
						    pass
					
					tree.write('new_news/' + newsFileName)
					#copy(dataSetPath + '/corpora/' + newsFileName, 'new_news/' + newsFileName)
				else:
					noNewsFile = True
				
				sentiments = []
				
				if noNewsFile == False:
					matrix, successRate = self.svmObject.getResult(parameters.baseFeatureType)
					
					totalSuccessRate += successRate
					
					for i in range(2):
						for j in range(2):
							if matrix[i][j] > 0:
								if j == 0:
									s = -1.0
								else:
									s = 1.0
								sentiments.append(s * matrix[i][j])
							else:
								pass
					
					currentSentiment = sum(sentiments) / (len(sentiments) * 1.0)
				
				else:
					pass
			
				sentimentList.append(currentSentiment)
			
				if noNewsFile == False:
					remove('new_news/' + newsFileName)
				else:
					pass
			
				streamTime += 1
				timeNow += datetime.timedelta(minutes = 15)
			
				if timeNow >= endingTime:
					break
			
			endTime = time.time()
			
			totalSuccessRate /= streamTime
			
			print 'Classification Success Rate : ', (totalSuccessRate * 100)
			print 'Total time taken for all classfication : %.2f minutes' %((endTime - startTime)/60)
			
			# trading engine
			tradingObject = TradingEngine(tradingDay, parameters.baseInvestAmount, parameters.baseKeepTime)
			tradingObject.getStockValuesForDay()
			
			tradingObject.runTrade('base', sentimentList)
			
			print 'Return Value for trade : ', tradingObject.returnValue
			
			choice = raw_input('Enter another date? (y/n) : ')