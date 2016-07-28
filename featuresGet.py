# Gets the features for the classification task

import xml.etree.ElementTree as ET
import pickle
from math import log
from os import listdir, remove
from os.path import isfile
from featureExtraction import FeatureExtraction
from featureSelection import FeatureSelection

#--------------------------------------------- GetFeatures Class ------------------------------------------

class GetFeatures:

	def __init__(self, dirPath):
		
		self.newsItems = []
		self.dirPath = dirPath
	
	
	def extractFeatures(self, featureType):
		
		# get list of the files in the corpus
		fileNames = listdir(self.dirPath)  
		
		if isfile('data/all_features.pkl'):
			remove('data/all_features.pkl')
		else:
			pass
		
		fileNames = [fileName for fileName in fileNames if fileName[-3:] == 'xml']
		
		# process each of the file in the corpus and get the body, sentiment
		for newsFile in fileNames:
			tree = ET.parse(self.dirPath + '/' + newsFile)
			root = tree.getroot()
			
			for item in root.findall('item'):
				
				# sentiment of the text
				sentiment = item.find("sentiment").text
		
				# body of the text
				newsBody = item.find("body").text
				
				if newsBody == None:
					print newsFile
				else:
					pass
				
				# feature extraction
				featureExtractionObject = FeatureExtraction(newsBody, sentiment)
			
				if featureType == 1:
					# feature extraction - bag of words
					featureExtractionObject.getBagOfWords()
			
				elif featureType == 2:
					# feature extraction - 2-gram
					featureExtractionObject.getTwoGrams()
				
				elif featureType == 3:
					# feature extraction - 2-word combinations
					featureExtractionObject.getTwoWordCombination()
			
				elif featureType == 4:		
					# feature extraction - proper noun phrases
					featureExtractionObject.getNounPhrases()
				
				self.newsItems.append((featureExtractionObject.featureDistribution, sentiment))	


	def selectFeatures(self, selectionType, numberOfFeatures):
		
		featureSelectionObject = FeatureSelection(self.newsItems, numberOfFeatures)
		featureSelectionObject.prologue()
		featuresSelected = True
		
		if selectionType == 1:
			featureSelectionObject.chiSquareSelection()
		
		elif selectionType == 2:
			featureSelectionObject.bnsSelection()
		
		else:
			featuresSelected = False
		
		if featuresSelected == True:
			fileWriter = open('data/best_features.pkl', 'w')
			for feature in featureSelectionObject.selectedFeatures:
				pickle.dump(feature, fileWriter)
			fileWriter.close()
		else:
			pass
	

	def representFeatures(self, haveToFormVector = False):
		
		# Loads the best features from the file
		bestFeatures = []
		fileReader = open('data/best_features.pkl', 'r')
		while True:
			try:
				bestFeatures.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		length = len(bestFeatures)
		numberOfDocumentsAppeared = [0] * length
		index = 0
		
		for feature in bestFeatures:
			for (frequencyDistribution, sentiment) in self.newsItems:
				if feature in frequencyDistribution:
					numberOfDocumentsAppeared[index] += 1
			index += 1
		
		# Opening a file to write the document vectors in it
		fileWriter = open('data/feature_set.data', 'w')
		
		# total number of document vectors being saved
		numberOfDocumentVectors = 0
		
		for (frequencyDistribution, sentiment) in self.newsItems:
			stringVector = ''
			
			if sentiment == 'positive':
				stringVector += '+1'
			elif sentiment == 'negative':
				stringVector += '-1'
			elif sentiment == 'neutral':
				stringVector += '+0'
			
			weights = []
			
			featurePresent = False	
			index = 0
			
			for feature in bestFeatures:
				if feature in frequencyDistribution:
					featurePresent = True
					frequency = frequencyDistribution[feature]
					maximumFrequency = frequencyDistribution[frequencyDistribution.max()]
					
					tfValue = 0.5 + ((0.5 * frequency) / maximumFrequency) 
					idfValue = log(len(self.newsItems) / (1.0 + numberOfDocumentsAppeared[index]))
					weights.append((tfValue * idfValue))
				else:
					weights.append(0.0)
				
				index += 1
			
			if featurePresent == True or haveToFormVector == True:
				fileWriter.write(stringVector)
				maximumValue = max(weights)
				minimumValue = min(weights)
				denominator = maximumValue - minimumValue
				
				k = 0
				while k < length:
					if denominator != 0.0:
						fileWriter.write(',' + str(round(((weights[k] - minimumValue) / denominator),3)))
					else:
						fileWriter.write(', 0.0')
					k += 1
				
				numberOfDocumentVectors += 1
				fileWriter.write("\n")
			
			featurePresent = False
		
		fileWriter.close()
		return numberOfDocumentVectors
