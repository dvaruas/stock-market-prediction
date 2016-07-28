# mock trading system

# BSE timings:
# pre-open 9 - 9:15
# continuous 9:15 - 3:30
# closing 3:30 - 3:40
# post close 3:40 - 4:00

import datetime
from os import remove
from os.path import isdir
from shutil import copy
import pickle
import time
import xml.etree.ElementTree as ET
from kmeans import KMeans
from ann import AnnValue
from projClustering import ProjectedClustering
from featuresGet import GetFeatures
import parameters

#-------------------------------------------- Mock Trade Class ----------------------------------------------

class PredictionModel:

	def __init__(self, date):
		
		self.dateOfTrade = date
		self.annObject = AnnValue()
		self.projectedClusteringObject = None
	
	
	def preConfigureModel(self):
		
		configureStart = time.time() # the pre-configuration starting time
		
		# get the previous trading day
		yesterday = self.dateOfTrade
		while True:
			yesterday -= datetime.timedelta(days = 1)
			datasetPath = 'dataset/' + yesterday.strftime('%d-%h-%G')
			if isdir(datasetPath):
				break
			else:
				continue
		
		try:
			remove('data/all_features.pkl')
		except:
			pass
		
		print 'Pre-Configuration stage, on date :', yesterday
		
		# the last day best features and last day points are saved 
		featureObject = GetFeatures(datasetPath + '/corpora')
		
		extractionStart = time.time()
		featureObject.extractFeatures(parameters.ourFeatureType) # 2-word combinations fe method
		extractionEnd = time.time()
		
		print '\nFeature Extraction time : %.2f minutes' %((extractionEnd - extractionStart)/60)
		
		selectionStart = time.time()
		featureObject.selectFeatures(parameters.ourSelectionType, parameters.initialNumberOfFeatures) # bns fs method, no of features
		selectionEnd = time.time()
		
		print 'Feature Selection time : %.2f minutes' %((selectionEnd - selectionStart)/60)
		
		numberOfVectors = featureObject.representFeatures()
		print 'Document vectors formed .. '
		
		copy('data/best_features.pkl', 'data/all_best_features.pkl')
		
		#------------------------------------ K-means Running ---------------------------------------
		
		print '\nRunning K-means ..'
		
		kmeansStart = time.time()
		
		kmeansObject = KMeans()
		kmeansObject.getDataPoints()
		kmeansObject.getInitialCenters()
		
		iterationNumber = 1
		notConverged = True
		
		while notConverged == True and iterationNumber < parameters.maximumIterations :
			timeNow = time.time()
			
			if iterationNumber % 20 == 0:
				print '..Iteration Number : %3d Time Elapsed till now : %.2f minutes' %(iterationNumber, (timeNow - kmeans_start) / 60.0)
			else:
				pass
			
			kmeansObject.assignToCluster()
			notConverged = kmeansObject.recalculateCentroids()
			
			iterationNumber += 1
		
		kmeansObject.saveClusters()

		kmeansEnd = time.time()
		
		print 'Kmeans running time : %.2f minutes' %((kmeansEnd - kmeansStart)/60)
		
		#-------------------------------------------------------------------------------------------------------
		
		# cluster info
		fileReader = open('data/cluster_info.pkl', 'r')
		clusterInfo = pickle.load(fileReader)
		fileReader.close()
		
		# for projected clustering
		print '\nPreparing the initial fading clusters ..'
		projectedClusteringStart = time.time()
		
		self.projectedClusteringObject = ProjectedClustering()
		self.projectedClusteringObject.prepareFadingClusters(clusterInfo)
		
		projectedClusteringEnd = time.time()
		
		print 'Fading clusters preparation time : %.2f minutes' %((projectedClusteringEnd - projectedClusteringStart) / 60)
		
		# take the last 10 files of 'yesterday' and store in the 'last' folder
		lastFileNames = []
		
		fileReader = open(datasetPath + '/log_file.txt', 'r')
		for line in fileReader:
			lastFileNames.append(line.split(' ')[0])
		fileReader.close()
		
		fileWriter = open('last/log.txt', 'w') # write the names of files
		
		lastFileNames = lastFileNames[-10:]
		for fileName in lastFileNames:
			try:
				copy(datasetPath + '/corpora/' + fileName, 'last/' + fileName)
			except:
				pass
			fileWriter.write(fileName + '\n')
		
		fileWriter.close()
		
		# get the ann ready
		self.annObject.loadAnnWeights()
		
		print '\nANN locked and loaded ..'
		
		configureEnd = time.time()
		
		print "Total time taken to pre-configure : %.2f minutes" %((configureEnd - configureStart)/60)
	
	
	def tradeRun(self, runAll):
		
		ch = None
		
		datasetPath = 'dataset/' + self.dateOfTrade.strftime('%d-%h-%G')
		
		previousSentiment = 0.0 # 0 standing for neutral
		currentSentiment = 0.0
		streamTime = 0 # considering this as 9:30 am
		timeNow = datetime.datetime.combine(self.dateOfTrade, datetime.time(9,15))
		endingTime = datetime.datetime.combine(self.dateOfTrade, datetime.time(15,15))
		numberOfCorrectSentiments = 0
		
		sentimentDictionary = {'positive' : 1.0, 'negative' : -1.0, 'neutral' : 0.0}
		predictedValues = [] # list of predicted values
		originalValues = []  # list of the actual values perceived
		signCorrectCount = 0 # number of signs correctly predicted
		thePreviousSentiments = [] 
		
		while True:
			
			print '\nTime :', timeNow.strftime('%H:%M'), '\n'
			predictionStartTime = time.time()
			
			noNewsFile = False
			
			# get the file name which is the current news
			fileReader = open(datasetPath + '/log_file.txt', 'r')
			
			for lineNumber, line in enumerate(fileReader):
				
				if lineNumber == streamTime:
					newsFileName = line
				elif lineNumber == (streamTime + 1):
					annFileName = line
					break
				else:
					pass
			fileReader.close()
			
			# move the news file to the new_news folder
			newsFileTemp = newsFileName.split(' ')[:-1]
			if newsFileTemp[1] != '0':
				newsFileName = newsFileTemp[0]
				copy(datasetPath + '/corpora/' + newsFileName, 'new_news/' + newsFileName)
			else:
				noNewsFile = True
			
			# get the file name containing the ann data
			newsFileTemp = annFileName.split(' ')[:-1]
			
			if len(newsFileTemp) == 0:
				break
			else:
				annFileName = newsFileTemp[0]
			
			# determines whether the new point forms a new cluster
			newClusterFormed = False
			
			if noNewsFile == False:
				currentSentiment = self.projectedClusteringObject.processStream(streamTime)
				if currentSentiment == None:
					newClusterFormed = True
				else:
					pass
			else:
				pass
			
			if noNewsFile == True or newClusterFormed == True:
				checkPrevious = thePreviousSentiments[-parameters.lastToDetermineSentiment:]
				if len(checkPrevious) != 0:
					currentSentiment = sum(checkPrevious) / (len(checkPrevious) * 1.0)
				else:
					currentSentiment = 0.0
			else:
				pass
			
			# save the current sentiment to previous sentiment
			previousSentiment = currentSentiment
			
			# inputs to the ann
			tree = ET.parse(datasetPath + '/ann_data/' + annFileName)
			root = tree.getroot()
			
			bseChange = float(root[1][0].text) - float(root[0][0].text)
			exchangeChange = float(root[1][1].text) - float(root[0][1].text)
			oilChange = float(root[1][2].text) - float(root[0][2].text)
			goldChange = float(root[1][3].text) - float(root[0][3].text)
			actualSentiment = root[2].text # used to correctly put the prediction if wrongly predicted earlier
			
			inputs = [bseChange, exchangeChange, oilChange, goldChange, currentSentiment]
			
			if currentSentiment == sentimentDictionary[actualSentiment]:
				numberOfCorrectSentiments += 1
			else:
				pass
			
			# predict the ann value
			predictedOutput = self.annObject.getAnnResult(inputs)
			
			predictedValue = predictedOutput[0] + float(root[1][0].text)
			originalValue = float(root[3].text)
			predictionEndTime = time.time()
			
			print "..The predicted sensex value : %.2f" %predictedValue
			print "..Actual sensex value :", originalValue
			print "\n..Prediction time : %.2f minutes" %((predictionEndTime - predictionStartTime)/60)
			
			# Calculating Normalized Mean Square Error
			
			predictedValues.append(predictedValue)
			originalValues.append(originalValue)
			
			originalValuesMean = sum(originalValues) / len(originalValues) # mean of all original values
			
			numerator = 0.0
			denominator = 0.0
			
			for predictedValue, originalValue in zip(predictedValues, originalValues):
				numerator += (originalValue - predictedValue) ** 2
				denominator += (originalValue - originalValuesMean) ** 2
			try:
				normalizedError = numerator / denominator
			except:
				normalizedError = None
			
			# Calculating Sign Correctness Percentage
			
			if (originalValue - float(root[1][0].text)) > 0.0:
				actualUp = True
			else:
				actualUp = False
			
			if (predictedValue - float(root[1][0].text)) > 0.0:
				predictedUp = True
			else:
				predictedUp = False
			
			if actualUp == predictedUp:
				signCorrectCount += 1
			else:
				pass
			
			signCorrectPercentage = (signCorrectCount / ((streamTime + 1) * 1.0)) * 100
			
			# print the performance stastics till now
			
			print "\n.. Stats till now : "
			print "Normalized Mean Square Error :", normalizedError
			print "Sign Correctness Percentage : %.2f %%" %signCorrectPercentage 
			
			# save the actual sentiments for later usage	
			thePreviousSentiments.append(sentimentDictionary[actualSentiment])
			
			# prepare the clusters for the next data item
			if noNewsFile == True:
				self.projectedClusteringObject.prepareForNext(actualSentiment, None, True)
			else:
				self.projectedClusteringObject.prepareForNext(actualSentiment, newsFileName, True)
			
			streamTime += 1
			timeNow += datetime.timedelta(minutes = 15)
			
			if runAll == 'y':
				pass
			else:
				# predict the next news data?
				choice = raw_input("Next? (y/n) : ")
				if choice == 'y':
					pass
				else:
					break
			
			if timeNow >= endingTime:
				break
		
		#print '\nClassification Accuracy : ', ((numberOfCorrectSentiments * 100.0) / streamTime)
		
		#-------------------------------- Save Predicted and Original Values ------------------------------
		
		fileWriter = open('data/predictedGraphs/' + str(self.dateOfTrade) + '-d_graph.csv', 'w')
		
		theTime = datetime.datetime.combine(self.dateOfTrade, datetime.time(9,30))
		
		fileWriter.write('Time,Predicted,Actual\n')
		for predictedValue, originalValue in zip(predictedValues, originalValues):
			fileWriter.write(theTime.strftime('%H:%M') + ',' + str(predictedValue) + ',' + str(originalValue) + '\n')
			theTime += datetime.timedelta(minutes = 15)
		
		fileWriter.close()
