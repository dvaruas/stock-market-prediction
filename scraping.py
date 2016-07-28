from lxml import html
import urllib2
import xml.etree.ElementTree as ET
import datetime


class WebScraper:
	
	def __init__(self, time1, time2 = None):
		
		self.startTime = time1
		self.endTime = time2
	
	
	def getSensexValue(self):
		
		startingPage = 'http://www.moneycontrol.com/sensex/bse/sensex-live'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		value = tree.xpath("//div[@class = 'PT10']/div/strong/text()")
		
		return float(value[0])
	
	
	def getExchangeRate(self):
		
		startingPage = 'http://in.finance.yahoo.com/q?s=USDINR=X'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		value = tree.xpath("//span[@id = 'yfs_l10_usdinr=x']/text()")
		
		return float(value[0])
	
	
	def getOilPrice(self):
		
		startingPage = 'http://www.moneycontrol.com/commodity/crudeoil-price.html'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		try:
			value = tree.xpath("//span[@class = 'rd_30']/text()")
		except:
			value = tree.xpath("//span[@class = 'gr_30']/text()")
		
		return float(value[0])
	
	
	def getGoldPrice(self):
		
		startingPage = 'http://www.moneycontrol.com/commodity/gold-price.html'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		try:
			value = tree.xpath("//span[@class = 'rd_30']/text()")
		except:
			value = tree.xpath("//span[@class = 'gr_30']/text()")
		
		return float(value[0])
	
	
	def getStockData(self):
		
		startingPage = 'https://www.google.com/finance?cid=672865'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		value = tree.xpath("//span[@id = 'ref_672865_l']/text()")
		
		return value[0]
	

	def getNews(self, fileName, bothLimits = False):
		
		prefixUrl = 'http://economictimes.indiatimes.com'
		startingPage = 'http://economictimes.indiatimes.com/etlatestnews.cms'
		page = urllib2.urlopen(startingPage, timeout = 60)
		response = page.read()
		tree = html.fromstring(response)
		
		newsLinks = tree.xpath('//ul[@class = "data"]/li/a/@href')
		
		root = ET.Element("items")
		numberOfNews = 0
		
		# scrap data from each link
		for link in newsLinks:
			try:
				response = urllib2.urlopen(prefixUrl + link, timeout = 60)	
				newResponse = response.read()
				newTree = html.fromstring(newResponse)
			except:
				continue
			
			# contains the news body
			line = newTree.xpath('//div[@class = "Normal"]/text()')
			
			# contains the body of the news
			newsBody = ' '.join(line)
			
			if newsBody == None:
				continue
			else:
				pass
			
			# the time for the specific news
			time = newTree.xpath('//div[@class = "byline"]/text()')
			
			try:
				temp = str(time[0].split(',').pop(-1)).split('.')
				hrs = int(temp[0][-2:])
				mins = int(temp[1][:2])
				ap = temp[1][2:4]
			except:
				continue
			
			if ap == 'PM' and hrs != 12:
				hrs += 12
			else:
				pass
			
			dx = datetime.time(hrs, mins)
			
			flag = False
			# news came within timeframe
			if dx >= self.startTime.time():
				if bothLimits == True:
					if dx <= self.endTime.time():
						flag = True
					else:
						pass
				else:
					flag = True
				
				if flag == True:
					item = ET.SubElement(root, "item")
					
					numberOfNews += 1
					body = ET.SubElement(item, "body")
					body.text = newsBody
					
					sentiment = ET.SubElement(item, "sentiment")
					sentiment.text = 'none'
				else:
					pass
				
			else:
				pass
		
		if numberOfNews > 0:
			tree = ET.ElementTree(root)
			tree.write(fileName)
		else:
			pass
		
		return numberOfNews
