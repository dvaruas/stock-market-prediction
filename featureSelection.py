# Feature selection

import pickle
import math
from nltk.probability import ConditionalFreqDist
from scipy import stats
from helper import Helper
	
#---------------------------------------------- FeatureSelection Class ------------------------------------------

class FeatureSelection:

	def __init__(self, docListFd, count):
		
		self.listDocumentsFeatures = docListFd
		self.numberOfFeaturesSelected = count
		self.selectedFeatures = []
		self.allFeatures = []
		self.labelledWordFd = ConditionalFreqDist()
		self.totalDocumentsCount = {'positive':0, 'negative':0, 'neutral':0}
		self.helperObject = Helper()


	def prologue(self):
		
		fileReader = open('data/all_features.pkl', 'r')
		while True:
			try:
				self.allFeatures.append(pickle.load(fileReader))
			except:
				break
		fileReader.close()
		
		for (news, sentiment) in self.listDocumentsFeatures:
			for feature in news:
				self.labelledWordFd[sentiment].inc(feature)
				self.totalDocumentsCount[sentiment] += 1
	
	
	def chiSquareSelection(self):
		
		for feature in self.allFeatures:
			# row-wise storage of contingency matrix
			contingencyMatrix = [[0] * 3] * 2
			expectedValues = [[0.0] * 3] * 2
			chiValues = [0.0] * 6
			
			sentiments = ['positive', 'negative', 'neutral']
			
			# observed scores in the contingency matrix
			for i in range(len(sentiments)):
				sentiment = sentiments[i]
				contingencyMatrix[0][i] = self.labelledWordFd[sentiment][feature]
				contingencyMatrix[1][i] = self.totalDocumentsCount[sentiment] - contingencyMatrix[0][i]
			
			# totalSums at the right hand side
			sumFeature = sum(contingencyMatrix[0])
			sumNotFeature = sum(contingencyMatrix[1])
			totalFeatureSumCount = sumFeature + sumNotFeature
			totalFeatureSumCount *= 1.0
			
			# expected scores in the contingency matrix
			for i in range(len(sentiments)):
				sentiment = sentiments[i]
				expectedValues[0][i] = (self.totalDocumentsCount[sentiment] * sumFeature) / totalFeatureSumCount
				expectedValues[1][i] = (self.totalDocumentsCount[sentiment] * sumNotFeature) / totalFeatureSumCount
			
			j = 0
			for i in range(0, 2 * len(sentiments), 2):
				chiValues[i] = self.helperObject.getChiSquareValue(contingencyMatrix[0][j] , expectedValues[0][j])
				chiValues[i+1] = self.helperObject.getChiSquareValue(contingencyMatrix[1][j] , expectedValues[1][j])	
				j += 1
			
			# chi-sq value for all four possible outcomes
			chiValue = sum(chiValues)
			
			# calculate p-value for the chi-sq value, degrees of freedom = 2
			pValue = (1 - stats.chi2.cdf(chiValue , 2))
			
			# cut-off at p-value of 5%
			if pValue < 0.05:
				self.selected_features.append(feature)
			else:
				pass
		
		self.selectedFeatures.sort()
		self.selectedFeatures = self.selectedFeatures[:self.numberOfFeaturesSelected]
	
	
	def bnsSelection(self):
		
		featureFrequency = {}
		
		totalSum = 0
		for feature in self.allFeatures:
			featureFrequency[feature] = self.labelledWordFd['positive'][feature] + self.labelledWordFd['negative'][feature] + self.labelledWordFd['neutral'][feature]
			totalSum += featureFrequency[feature]
		
		# calculate mean
		mean = totalSum / (len(featureFrequency) * 1.0)
		
		# calculate standard deviation
		temp = 0.0
		for feature in self.allFeatures:
			temp += (featureFrequency[feature] - mean) ** 2
		temp = temp / len(featureFrequency)
		standardDeviation = math.sqrt(temp)
		
		# find total positive and negative messages
		totalPositive = self.totalDocumentsCount['positive']
		totalNegative = self.totalDocumentsCount['negative']
		totalNeutral = self.totalDocumentsCount['neutral']
		
		# calculate bns score for each feature
		bnsScores = {}
		for feature in self.allFeatures:
			scores = [0.0] * 3
			
			# positive vs. rest
			posScore = self.helperObject.getZScore(self.labelledWordFd['positive'][feature], totalPositive, mean, standardDeviation)
			negNeuScore = self.helperObject.getZScore(self.labelledWordFd['negative'][feature] + self.labelledWordFd['neutral'][feature], totalNegative + totalNeutral, mean, standardDeviation)
			scores[0] = math.fabs(posScore - negNeuScore)
			
			# negative vs. rest
			negScore = self.helperObject.getZScore(self.labelledWordFd['negative'][feature], totalNegative, mean, standardDeviation)
			posNeuScore = self.helperObject.getZScore(self.labelledWordFd['positive'][feature] + self.labelledWordFd['neutral'][feature], totalPositive + totalNeutral, mean, standardDeviation)
			scores[1] = math.fabs(negScore - posNeuScore)
			
			# neutral vs. rest
			neuScore = self.helperObject.getZScore(self.labelledWordFd['neutral'][feature], totalNeutral, mean, standardDeviation)
			posNegScore = self.helperObject.getZScore(self.labelledWordFd['negative'][feature] + self.labelledWordFd['positive'][feature], totalNegative + totalPositive, mean, standardDeviation)
			scores[2] = math.fabs(neuScore - posNegScore)
			
			# save the best among all the scores
			bnsScores[feature] = max(scores)
		
		self.selectedFeatures = [key for (key, value) in (sorted(bnsScores.iteritems(), key = lambda (key,value) : value, reverse = True))][:self.numberOfFeaturesSelected]