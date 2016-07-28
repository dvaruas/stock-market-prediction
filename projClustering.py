# Projected Clustering

import pickle
import time
from math import sqrt
from shutil import move
from copy import deepcopy
from os import rename, remove
import xml.etree.ElementTree as ET
from featuresGet import GetFeatures
from helper import Helper
import parameters
	
#------------------------------------------------- Clusters Class -----------------------------------------

class FadingCluster:

	def __init__(self, clusterCreationTime):
		
		self.dimensionVector = [] # the dimensions which are relevant at the moment
		self.fc2Measure = {} # fc2MeasureTempeasure {dimension : measure}
		self.fc1Measure = {} # fc1MeasureTempeasure {dimension : measure}
		self.weight = 0.0    
		self.lastUpdateTime = clusterCreationTime
		self.clusterCenter = {} # center {dimension : measure}
		self.sentimentCount = {'+1' : 0, '-1' : 0, '+0' : 0}
		self.helperObject = Helper()

	
	def changeFeatureSpace(self):
		
		# load the old feature set
		oldFeatureSet = []
		fileReader = open('data/all_best_features.pkl', 'r')
		while True:
			try:
				oldFeatureSet.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		# load the new evolved feature space
		newFeatureSet = []
		fileReader = open('data/best_features.pkl', 'r')
		while True:
			try:
				newFeatureSet.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		# save old measures for the evolved cluster
		fc2MeasureTemp = {}
		fc1MeasureTemp = {}
		centerTemp = {}
		dimensionVectorTemp = []
		
		for featureIndex in self.fc2Measure:
			featureName = oldFeatureSet[featureIndex]
			
			newIndex = newFeatureSet.index(featureName)
			dimensionVectorTemp.append(newIndex)
			
			fc2MeasureTemp[newIndex] = self.fc2Measure[featureIndex]
			fc1MeasureTemp[newIndex] = self.fc1Measure[featureIndex]
			centerTemp[newIndex] = self.clusterCenter[featureIndex]
		
		self.fc2Measure = dict(fc2MeasureTemp)
		self.fc1Measure = dict(fc1MeasureTemp)
		self.clusterCenter = dict(centerTemp)
		self.dimensionVetor = list(dimensionVectorTemp)

	
	def decayWithTime(self, currentTime):
		
		updatedValue = self.helperObject.fadingFunction(currentTime - self.lastUpdateTime)
		
		for key in self.fc1Measure:
			self.fc1Measure[key] *= updatedValue
			self.fc2Measure[key] *= updatedValue
		
		self.weight = self.weight * updatedValue
		self.lastUpdateTime = currentTime


	def addNewDataPoint(self, currentTime, allDataPoints = False, point = []):
		
		# allDataPoints = true for adding all the data points to a cluster
		# allDataPoints = false for adding one data point to the cluster
		
		if allDataPoints == True:
			fileReader = open('data/feature_set.data', 'r')
		elif allDataPoints == False:
			fileReader = [point]
		else:
			pass
		
		self.decayWithTime(currentTime)
		
		numberOfDataPoints = sum(self.sentimentCount.values())
		
		for k in self.clusterCenter:
			self.clusterCenter[k] *=  numberOfDataPoints
		
		for line in fileReader:
			if allDataPoints == True:
				weights = line.split(',')[1:]
			else:
				weights = line
			
			i = 0
			for weight in weights:
				weightValue = float(weight)
				
				if weightValue != 0.0:
					try:
						self.fc2Measure[i] += weightValue ** 2
						self.fc1Measure[i] += weightValue 
						self.clusterCenter[i] += weightValue
					except:
						self.fc2Measure[i] = weightValue ** 2
						self.fc1Measure[i] = weightValue 
						self.clusterCenter[i] = weightValue
				self.weight += 1.0
				i += 1
		
		for k in self.clusterCenter:
			self.clusterCenter[k] /= (numberOfDataPoints + 1)


	def computeRadius(self):
		
		radius = {}
		
		for fc2Value, fc1Value in zip(self.fc2Measure, self.fc1Measure):
			
			value = ((self.fc2Measure[fc2Value] / self.weight) - ((self.fc1Measure[fc1Value] / self.weight) ** 2))
			radius[fc2Value] = value
		
		return radius
	
#----------------------------------------- Projected Clustering Class ------------------------------------

class ProjectedClustering:

	def __init__(self):
		
		self.fadingClusters = []
		self.maximumClusters = parameters.maximumClusters
		self.numberOfClusters = 0
		self.dimensionsCount = parameters.dimensionality


	def getVectorsFromStream(self):
		
		# get features from last data chunks
		featureObject = GetFeatures('last')
		featureObject.extractFeatures(parameters.ourFeatureType)
		featureObject.selectFeatures(parameters.ourSelectionType, 1000)
		
		rename('data/best_features.pkl', 'data/last_bst_features.pkl')
		
		# the old features
		featuresOld = []
		fileReader = open('data/last_bst_features.pkl', 'r')
		while True:
			try:
				featuresOld.append(pickle.load(fileReader))
			except:
				break
		
		featuresOld = set(featuresOld)
		
		# feature extraction of new news
		featureObject = GetFeatures('new_news')
		featureObject.extractFeatures(parameters.ourFeatureType)
		
		# the feature selection process for new news
		featuresNew = []
		fileReader = open('data/all_features.pkl', 'r')
		while True:
			try:
				featuresNew.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		featuresNew = set(featuresNew)
		selectedFeatures = featuresNew.intersection(featuresOld)
		leftOverNewFeatures = featuresNew.difference(selectedFeatures)
		maximumOldFeatures = int(parameters.countNewFeatures * parameters.lastFeaturesPercent)
		
		featuresNew = []
		
		featureCount = {}
		for (featureDistribution, sentiment) in featureObject.newsItems:
			for feature in featureDistribution:
				if feature in leftOverNewFeatures:	
					try:
						featureCount[feature] += 1
					except:
						featureCount[feature] = 1
				else:
					pass
		
		sortedFeatures = sorted(featureCount, key = lambda p : featureCount[p], reverse = True)
		
		def findIndex(featureName):
			try:
				return sortedFeatures.index(featureName)
			except:
				return 99
		
		selectedFeatures = sorted(selectedFeatures, key = lambda key : findIndex(key))[:maximumOldFeatures]
		
		newFeatures = selectedFeatures
		
		stillLeft = parameters.countNewFeatures - len(selectedFeatures)
		
		newSetFeatures = sorted(leftOverNewFeatures, key = lambda key : findIndex(key))[:stillLeft]
		
		newFeatures += newSetFeatures
		
		# previous feature space
		totalFeatures = []
		fileReader = open('data/all_best_features.pkl', 'r')
		while True:
			try:
				totalFeatures.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		# homogeneous conversion of feature space
		newSet = set(totalFeatures).union(set(newFeatures))
		featureSpace = list(newSet)
		
		# new feature space
		fileWriter = open('data/best_features.pkl', 'w')
		for feature in featureSpace:
			pickle.dump(feature, fileWriter)
		fileWriter.close()
		
		# feature representation of new news
		featureObject.representFeatures()
	
	
	def prepareFadingClusters(self, initialClusterInfo):
		
		# save all initial points in the 'points' dictionary
		points = {} # {pointIndex : pointDictionary}
		pointIndex = 0
		
		fileReader = open('data/feature_set.data', 'r')
		for line in fileReader:
			currentPoint = {} # {'s':sentiment, dimesion1 : measure, ... }
			values = line.split(',')
			
			currentPoint['sentiment'] = values.pop(0) # stores the sentiment
			
			weights = [float(w) for w in values] # stores the weights
			
			i = 0
			for w in weights:
				if w != 0.0:
					currentPoint[i] = w
				i += 1
				
			points[pointIndex] = currentPoint
			
			pointIndex += 1
		
		fileReader.close()
		
		iterationNumber = 0
		sumInThisIteration = []
		convergence = False
		
		# find initial fading clusters
		while True:
			startFadingPreparation = time.time()
			
			print 'Iteration : %3d' %iterationNumber, 
			
			self.fadingClusters = []
			
			# total number of clusters
			self.numberOfClusters = len(initialClusterInfo)
			
			# form the fading cluster objects
			for i in range(self.numberOfClusters):
				clusterObject = FadingCluster(0)
				self.fadingClusters.append(clusterObject)
			
			# save the measures in the clusters
			for point in points:
				pointDictionary = dict(points[point])
				belongsToClusterNumber = -1
				
				i = 0
				for cluster in initialClusterInfo:
					if point in cluster:
						belongsToClusterNumber = i
						break
					else:
						pass
					
					i += 1
				
				clusterObject = self.fadingClusters[belongsToClusterNumber]
				
				tempDictionary = dict(points[point])
				
				for i in tempDictionary:
					if i == 'sentiment':
						continue
					else:
						pass
					
					weight = tempDictionary[i]
					
					try:
						clusterObject.fc2Measure[i] += (weight ** 2)
						clusterObject.fc1Measure[i] += weight
						clusterObject.clusterCenter[i] += weight
					except:
						clusterObject.fc2Measure[i] = (weight ** 2)
						clusterObject.fc1Measure[i] = weight
						clusterObject.clusterCenter[i] = weight
				clusterObject.weight += 1.0
				
				sentiment = currentPoint['sentiment']
				clusterObject.sentimentCount[sentiment] += 1
			
			totalDimensions = self.dimensionsCount * self.numberOfClusters
			
			smallest = [] # information saved as : [radius value, cluster no, dimension no]
			
			# find the radius of each cluster, append least 2 radius dimensions of each cluster
			radii = []
			clusterNumber = 0
			
			for clusterObject in self.fadingClusters:
				
				radiiEachCluster = clusterObject.computeRadius()
				radii.append(radiiEachCluster)
				
				smallest2Keys = sorted(radiiEachCluster, key = lambda key : radiiEachCluster[key])[:2]
				for i in smallest2Keys:
					smallest.append([radiiEachCluster[i], clusterNumber, i])
				
				clusterNumber += 1
			
			i = alreadyFound = (clusterNumber * 2)
			
			while i < totalDimensions:
				smallest.append([float('inf'), 0, 0])
				i += 1
			
			
			# find the smallest radiuses from all the radius, to determine rest of the dimensions
			
			i = 0
			maximumInSmallest = max(smallest[alreadyFound :], key = lambda p : p[0])
			
			for radiiEachCluster in radii:
				for radius in radiiEachCluster:
					flag = True
					
					formedValue = [radiiEachCluster[radius], i, radius]
					for x in smallest[:alreadyFound]:
						if x == formedValue:
							flag = False
						else:
							pass
					
					if flag == True and radiiEachCluster[radius] < maximumInSmallest[0]:
						indx = smallest.index(maximumInSmallest)
						smallest[indx] = formedValue
						maximumInSmallest = max(smallest[alreadyFound :], key = lambda p : p[0])
					else:
						pass
				i += 1
			
			bitDimensions = []
			for i in range(self.numberOfClusters):
				bitDimensions.append([])
		
			for eachValue in smallest:
				bitDimensions[eachValue[1]].append(eachValue[2])
			
			
			# save centerTempoid and dimensions in each cluster
			i = 0
			for clusterObject in self.fadingClusters:
				denominator = sum(clusterObject.sentimentCount.values())
				
				for centerDim in clusterObject.clusterCenter:
					clusterObject.clusterCenter[centerDim] /= denominator
				
				clusterObject.dimensionVetor = list(bitDimensions[i])
				i += 1
			
			adder = []
			for clusterObject in self.fadingClusters:
				adder.append(sum(clusterObject.clusterCenter.values()))
			sumInThisIteration.append(sum(adder))
			
			if (len(sumInThisIteration) >=4) and (sumInThisIteration[-2:] == sumInThisIteration[-4:-2]):
				convergence = True
			else:
				pass
			
			# the terminating condition for the while loop
			if iterationNumber > 500 or convergence == True:
				print 'Fading clusters converged .. '
				break
			else:
				pass
			
			newClusterPoints = {}
			# find the distance of each point from each cluster centerTempoid along projected dimensions
			for point in points:
				distance = []
				for clusterObject in self.fadingClusters:
					distance.append(self.findProjectedDistance(clusterObject, clusterObject.dimensionVetor, points[point]))
				
				minimumDistance = min(distance)
				indx = distance.index(minimumDistance)
				
				try:
					newClusterPoints[indx].append(point)
				except:
					newClusterPoints[indx] = [point]
			
			# save the new cluster points		
			initialClusterInfo = []
			for cPoint in newClusterPoints:
				initialClusterInfo.append(newClusterPoints[cPoint])
			
			endFadingPreparation = time.time()
			
			print 'Time taken : %.2f minutes' %((endFadingPreparation - startFadingPreparation) / 60)
			
			iterationNumber += 1
	
	
	def computeDimensions(self, streamTime):
		
		self.numberOfClusters = len(self.fadingClusters)
		
		tentativeFadingClusters = deepcopy(self.fadingClusters)
		for clusterObject in tentativeFadingClusters:
			clusterObject.addNewDataPoint(streamTime, True)
		
		totalDimensions = self.dimensionsCount * self.numberOfClusters
		
		# value, cluster no, dimension no
		smallest = []
		for i in range(totalDimensions):
			smallest.append([float('inf'), 0, 0])
		
		radii = []
		for clusterObject in tentativeFadingClusters:
			radii.append(clusterObject.computeRadius())
		
		i = 0
		
		maximumInSmallest = max(smallest, key = lambda p : p[0])
		
		
		for radiiEachCluster in radii:
			for radius in radiiEachCluster:
				if radiiEachCluster[radius] < maximumInSmallest[0]:
					indx = smallest.index(maximumInSmallest)
					smallest[indx] = [radiiEachCluster[radius], i, radius]
					maximumInSmallest = max(smallest, key = lambda p : p[0])
				else:
					pass
			i += 1
		
		bitDimensions = []
		for i in range(self.numberOfClusters):
			bitDimensions.append([])
		
		for sList in smallest:
			bitDimensions[sList[1]].append(sList[2])
		
		return bitDimensions


	def findProjectedDistance(self, clusterObject, dimension, newDataPoint):
		
		distance = 0.0
		
		for d in dimension:
			if d in clusterObject.clusterCenter:
				x1 = clusterObject.clusterCenter[d]
			else:
				x1 = 0.0
			
			if d in newDataPoint:
				x2 = newDataPoint[d]
			else:
				x2 = 0.0
			
			distance += abs(x1 - x2)
		
		numberOfDimensions = len(dimension)
		
		try:
			distance /= numberOfDimensions
		except:
			distance = float('inf')
		
		return distance

	
	def findLimitingRadius(self, clusterObject):
		
		radius = clusterObject.computeRadius()
		
		capitalR = 0.0
		for d in clusterObject.dimensionVector:
			try:
				capitalR += r[d]
			except:
				pass
		
		dimensionLength = len(clusterObject.dimensionVector)
		try:
			radius = sqrt(capitalR / dimensionLength)
		except:
			radius = float('inf')
		
		return (radius * parameters.spreadRadiusFactor)

	
	def addFadingCluster(self, point, time):
		
		clusterObject = FadingCluster(time)
		clusterObject.addNewDataPoint(time, 0, point)
		self.fadingClusters.append(clusterObject)
		self.numberOfClusters += 1

	
	def processStream(self, streamTime):
		
		# form document vectors of latest data chunk
		conversionStart = time.time()
		self.getVectorsFromStream()
		conversionEnd = time.time()
		print "Time taken to create document vectors : %.2f minutes .." %((conversionEnd - conversionStart)/60.0)
		
		print '\nChanging feature space of the fading clusters ..\n'
		
		# change the fading clusters according to the new feature space
		for clusterObject in self.fadingClusters:
			clusterObject.changeFeatureSpace()
		
		sentiment = []
		
		fileReader = open('data/feature_set.data', 'r')
		for vectors in fileReader:
			
			dimensions = self.computeDimensions(streamTime)
			self.numberOfClusters = len(self.fadingClusters)
			
			i = 0
			for d in dimensions:
				self.fadingClusters[i].dimensionVector = d
				i += 1
			
			point = vectors.split(',')[1:]
			point = [float(p) for p in point]
			
			clusterDimensions = [0.0] * self.numberOfClusters
			for i in range(self.numberOfClusters):
				clusterDimensions[i] = self.findProjectedDistance(self.fadingClusters[i], dimensions[i], point)
			
			clusterIndex = clusterDimensions.index(min(clusterDimensions))
			
			limitRadius = self.findLimitingRadius(self.fadingClusters[clusterIndex])
			
			if clusterDimensions[clusterIndex] > limitRadius:
				index = len(self.fadingClusters) + 1
				self.addFadingCluster(point, streamTime)
			else:
				self.fadingClusters[clusterIndex].addNewDataPoint(streamTime, 0, point)
				maximumValue = -1
				maximumKey = 0
				for key, value in self.fadingClusters[clusterIndex].sentimentCount.iteritems():
					if value > maximumValue:
						maximumValue = value
						maximumKey = key
					else:
						pass
				
				sentiment.append(maximumKey)
				
				self.fadingClusters[clusterIndex].sentimentCount[maximumKey] += 1
		
		positiveCount = sentiment.count('+1')
		negativeCount = sentiment.count('-1') 
		neutralCount = sentiment.count('+0')
		totalCount = positiveCount + negativeCount + neutralCount 
		
		# pos multiplied by 0, neg multiplied by -1, neu multiplied by 0
		try:
			streamSentiment = (positiveCount - negativeCount) / (totalCount * 1.0)
		except:
			streamSentiment = None
		
		return streamSentiment


	def prepareForNext(self, previousActualSentiment, fileName = None, mockTrade = False):
		
		# removes clusters which have zero dimensions assigned to them
		removeClusters = []
		
		for clusterObject in self.fadingClusters:
			
			if len(clusterObject.dimensionVector) == 0:
				removeClusters.append(clusterObject)
			else:
				pass
		
		for clusterObject in removeClusters:
			self.fadingClusters.remove(clusterObject)
		
		self.numberOfClusters = len(self.fadingClusters)
		
		# removes the least recently updated cluster if number of clusters becomes more than maximum number of clusters	
		if self.numberOfClusters > self.maximumClusters:
			updateTimes = [clusterObject.lastUpdateTime for clusterObject in self.fadingClusters]
			index = updateTimes.index(min(updateTimes))
			self.fadingClusters.pop(index)
		else:
			pass
		
		# find out the new clusters with single point and record their sentiment
		for clusterObject in self.fadingClusters:
			if sum(clusterObject.sentimentCount.values()) == 0:
				if previousActualSentiment == 'positive':
					clusterObject.sentimentCount['+1'] += 1
				elif previousActualSentiment == 'negative':
					clusterObject.sentimentCount['-1'] += 1
				else:
					clusterObject.sentimentCount['+0'] += 1
			else:
				pass
		
		print 'Clusters present : '
		# print the clusters
		for clusterObject in self.fadingClusters:
			print clusterObject.dimensionVector, clusterObject.sentimentCount
		
		
		if fileName != None:
			# puts the sentiment values in the news	
			tree = ET.parse('new_news/' + fileName)
			root = tree.getroot()
			for sentimentNode in root.iter('sentiment'):
				sentimentNode.text = previousActualSentiment
			
			# move the new news to the last folder
			tree.write('last/' + fileName)
			remove('new_news/' + fileName)
			
			# put entry of the file in log
			try:
				fileReader = open('last/log.txt', 'r')
			except:
				pass
			finally:
				fileWriter = open('last/log_temp.txt', 'w')
				
				oldestFile = fileReader.readline()[:-1]
				
				for line in fileReader:
					fileWriter.write(line)
				fileWriter.write(fileName + '\n')
				
				try:
					fileReader.close()
					remove('last/log.txt')
				except:
					pass
				fileWriter.close()
			
			rename('last/log_temp.txt', 'last/log.txt')
			
			try:
				remove('last/' + oldestFile)
			except:
				pass

		if fileName != None:
			# save current feature set as the total best feature set
			rename('data/best_features.pkl', 'data/all_best_features.pkl')
		else:
			pass
