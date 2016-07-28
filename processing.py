from nltk import stem, word_tokenize # for the stemming 
import xml.etree.ElementTree as ET # for xml tree
from nltk.corpus import stopwords  # for removing stopwords from the text
import re
from os import remove

#--------------------------------------------------------------------------------------------------------------

class PreProcessor:
	
	def __init__(self):
		
		self.porterStemmer = stem.porter.PorterStemmer()
	
	
	def processing(self, fileName):
		
		tree = ET.parse(fileName)
		root = tree.getroot()
		
		for body in root.iter('body'):
			try:
				bodyText = str(body.text)
			except:
				continue
			
			# converting to lower case
			bodyText = bodyText.lower()
			
			# removing all punctuation marks from the text body
			bodyText = re.sub('[/*?,!:=%;()0-9$\'\^<>"]', '', bodyText)
			
			# breaking the text body into seperate word tokens
			wordTokens = word_tokenize(bodyText)
			
			stemmedWords = []
			
			for eachWordToken in wordTokens:
				stemmedWords.append(self.porterStemmer.stem(eachWordToken))
				
				# if word is a stopword then remove it
				if eachWordToken in stopwords.words('english'):
					stemmedWords.pop()                    
			
			body.text = ' '.join(stemmedWords)
		
		remove(fileName)
		tree.write(fileName)
