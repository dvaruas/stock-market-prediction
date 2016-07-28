from os import mkdir, remove
import datetime
import xml.etree.ElementTree as ET
from scraping import WebScraper
from processing import PreProcessor
from time import sleep, strftime
	
#---------------------------------------------- DataCollector class ------------------------------------------		

class DataCollector:
	
	def __init__(self):
		
		self.scraperObject = WebScraper(None)
		self.processorObject = PreProcessor()
		self.dataCorpusPath = None
		self.dataAnnPath = None
		self.stockValuesFileName = strftime('%d-%h-%G') + '.xml'


	def waitForNext(self, deadline):
		
		while (int(strftime('%M')) % 15) != deadline:
		    sleep(60)
	
	
	def scrapAllData(self):
		
		valueDictionary = {}
		
		valueDictionary['bse'] = self.scraperObject.getSensexValue() # Get sensex value
		valueDictionary['exchange'] = self.scraperObject.getExchangeRate() # Get exchange rate
		valueDictionary['oil'] = self.scraperObject.getOilPrice() # Get oil price
		valueDictionary['gold'] = self.scraperObject.getGoldPrice() # Get Gold price
		
		return valueDictionary
	
	
	def defineNodeChildren(self, parentNode, valueDictionary):
		
		bseNode = ET.SubElement(parentNode, "bse")
		bseNode.text = str(valueDictionary['bse'])
		
		exchangeNode = ET.SubElement(parentNode, "exchange")
		exchangeNode.text = str(valueDictionary['exchange'])
		
		oilNode = ET.SubElement(parentNode, "oil")
		oilNode.text = str(valueDictionary['oil'])
		
		goldNode = ET.SubElement(parentNode, "gold")
		goldNode.text = str(valueDictionary['gold'])    
	
	
	def saveValuesToFile(self, fileName, previousDictionary, currentDictionary, sentiment, bseValueAfter15):
		
		newRootNode = ET.Element("values")
		
		beforeNode = ET.SubElement(newRootNode, "before15")
		self.defineNodeChildren(beforeNode, previousDictionary)
		
		currentNode = ET.SubElement(newRootNode, "current")
		self.defineNodeChildren(currentNode, currentDictionary)
		
		sentimentNode = ET.SubElement(newRootNode, "sentiment")
		sentimentNode.text = sentiment
		
		afterNode = ET.SubElement(newRootNode, "after15")
		afterNode.text = str(bseValueAfter15)
		
		newTree = ET.ElementTree(newRootNode)
		newTree.write(self.dataAnnPath + '/' + fileName)
	
	
	def modifyNewsSentiment(self, fileToModify, sentiment):
		
		tree = ET.parse(fileToModify)
		root = tree.getroot()
		
		for senti in root.iter('sentiment'):
			senti.text = sentiment
		
		tree.write(self.dataCorpusPath + '/' + fileToModify)
		remove(fileToModify)
	
	
	def saveStockValue(self, valueNow, timeNow):
		
		try:
			stockValueFile = ET.parse('stock_quotes/' + self.stockValuesFileName)
			root = stockValueFile.getroot()
		except:
			root = ET.Element('TSValues')
		
		valueNode = ET.Element('value')
		valueNode.set('time', timeNow.strftime('%H:%M'))
		valueNode.text = valueNow
		
		root.append(valueNode)
		
		tree = ET.ElementTree(root)
		tree.write('stock_quotes/' + self.stockValuesFileName)
		
		print 'Stock Value saved.. \n'
	
	
	def dataGather(self):
		
		folderName = strftime('%d-%h-%G') # day-month-year
		pathOfData = 'dataset/' + folderName
		self.dataCorpusPath = pathOfData + '/corpora'
		self.dataAnnPath = pathOfData + '/ann_data'
		try:
			mkdir(pathOfData)
			mkdir(self.dataCorpusPath)
			mkdir(self.dataAnnPath)
		except:
			pass
			
		# to make it wait till exactly 9:00 am
		self.waitForNext(0)
		
		# time = 9:00 am
		startTime = datetime.datetime.now()
		self.scraperObject.startTime = startTime
		timeNow = startTime
		
		# Get the Sensex value, exchange, oil price, gold price 15 minutes before news collection
		previousValuesDictionary = self.scrapAllData()
		
		previousCount = None
		previousFileName = None
		countNews = 0
		
		i = 0
		while timeNow.time() < datetime.time(15, 30):
			
			stockValue = self.scraperObject.getStockData()
			self.saveStockValue(stockValue, timeNow)
			
			bseBefore15Value = previousValuesDictionary['bse']
			
			print 'Timeframe : ', i, ' Time : ', datetime.datetime.now().time()
			
			self.waitForNext(5) # the 5 minute waiter
			
			print '\n..Minutes passed = 5 minutes..'
			bseAfter5Value = self.scraperObject.getSensexValue()
	
			self.waitForNext(10) # the 5 minute waiter
			
			print '..Minutes passed = 10 minutes..'
			bseAfter10Value = self.scraperObject.getSensexValue()
			
			self.waitForNext(0) # the 5 minute waiter
			
			print '..Minutes passed = 15 minutes..'
			currentValuesDictionary = self.scrapAllData()
			bseCurrentValue = currentValuesDictionary['bse']
			
			print '\n..Collecting News released in 15 minutes window..\n'
			fileName = strftime('%d-%m-%y-%H:%M:%S') + '.xml'  # day month year hour minute second
			countNews = self.scraperObject.getNews(fileName)
			
			fileWriter = open(pathOfData + '/log_file.txt', 'a') # log file
			fileWriter.write(fileName + ' ' + str(countNews) + ' ' + '\n')
			fileWriter.close()
			
			if countNews > 0:
				self.processorObject.processing(fileName)
			else:
				pass
			
			print "Change in 0 - 5 minutes :", str(bseAfter5Value - bseBefore15Value)
			print "Change in 5 - 10 minutes :", str(bseAfter10Value - bseAfter5Value)
			print "Change in 10 - 15 minutes :", str(bseCurrentValue - bseAfter10Value)
			
			change = (bseAfter5Value - bseBefore15Value)*0.5 + (bseAfter10Value - bseAfter5Value)*0.3 + (bseCurrentValue - bseAfter10Value)*0.2
			
			# find sentiment according to market analysis, 5 threshold
			if change < 0.0:
				sentiment = 'negative'
			else:
				if change >= 5.0:
					sentiment = 'positive'
				else:
					sentiment = 'neutral'
			
			if i != 0:
				if previousCount > 0:	
					self.modifyNewsSentiment(previousFileName, sentiment)
				else:
					pass
				
				self.saveValuesToFile(fileName, previousValuesDictionary2, previousValuesDictionary, sentiment, bseCurrentValue)
			
			previousValuesDictionary2 = dict(previousValuesDictionary)
			previousValuesDictionary = dict(currentValuesDictionary)
			
			timeNow = datetime.datetime.now()
			self.scraperObject.startTime = timeNow
			
			print '\n---------------------------------------------------------------------------\n'
			
			previousCount = countNews
			previousFileName = fileName
			i += 1
		
		if countNews > 0:
			remove(fileName)
		else:
			pass
			
		stockValue = self.scraperObject.getStockData()
		self.saveStockValue(stockValue, timeNow)
