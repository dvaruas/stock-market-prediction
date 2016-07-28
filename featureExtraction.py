# Feature Extraction methods

from nltk.util import ngrams
from nltk.tag import pos_tag 
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.chunk.regexp import RegexpParser
from helper import Helper
	
#--------------------------------------------- Feature Extraction Class ------------------------------------------

class FeatureExtraction:

	def __init__(self, newsBody, sentiment):
		
		self.sentences = [sentence.strip() for sentence in newsBody.split(".")][:-1]
		self.sentiment = sentiment
		self.featureDistribution = FreqDist()
		self.helperObject = Helper()	

	
	def convertToFeatureDist(self, featureSet):
		
		for feature in featureSet:
			self.featureDistribution.inc(feature)
	

	def getBagOfWords(self):
		
		featureSet = []
		
		for sentence in self.sentences:
			wordsInSentence = sentence.split(' ')
			featureSet += wordsInSentence
		
		self.convertToFeatureDist(featureSet)
		self.helperObject.saveAllFeaturesExtracted(featureSet)

	
	def getTwoGrams(self):
		
		featureSet = []
		
		for sentence in self.sentences:
			wordsInSentence = sentence.split(' ')
			twoGrams = ngrams(wordsInSentence, 2)
			
			for twoGram in twoGrams:
				gramFeature = twoGram[0] + ' ' + twoGram[1]
				featureSet.append(gramFeature)
		
		self.convertToFeatureDist(featureSet)
		self.helperObject.saveAllFeaturesExtracted(featureSet)


	def getTwoWordCombination(self):
		
		featureSet = []
		
		for sentence in self.sentences:
			wordsInSentence = sentence.split(' ')
			lengthOfSentence = len(wordsInSentence)
			
			for i in range(2, lengthOfSentence + 1, 1):
				nGrams = ngrams(wordsInSentence, i)
				
				for nGram in nGrams:
					gramFeature = nGram[0] + " " + nGram[-1]
					featureSet.append(gramFeature)
		
		self.convertToFeatureDist(featureSet)
		self.helperObject.saveAllFeaturesExtracted(featureSet)


	def getNounPhrases(self):
		
		featureSet = []
		
		# Handbook of NLP - Multiword Expressions, Timothy Baldwin and Su Nam Kim
		grammar = r"""
		    NBAR:
		    {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
		    NP:
		    {<NBAR>}
		    {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
		"""
		chunker = RegexpParser(grammar)
	
		for sentence in self.sentences:
			tokens = word_tokenize(sentence)
			
			if len(tokens) == 0:
				continue
			else:
				pass
			
			tagged = pos_tag(tokens)
			tree = chunker.parse(tagged)
			terms = []
			leafCollection = []
			
			for subtree in tree.subtrees(filter = lambda t : t.node == 'NP'):
				leafCollection.append(subtree.leaves())
			
			for leaf in leafCollection:
				term = [w for w,t in leaf if len(w) > 2]
				phrase = ' '.join(term)
				terms.append(phrase)
			
			featureSet += terms
		
		self.convertToFeatureDist(featureSet)
		self.helperObject.saveAllFeaturesExtracted(featureSet)