# Trading engine

import xml.etree.ElementTree as ET

#--------------------------------------------- Trading Engine ------------------------------------------

class TradingEngine:
    
    def __init__(self, tradingDate, amountInvested, keepTime):
        
        self.returnValue = 0.0
        self.tradingDate = tradingDate
        self.amountInvested = amountInvested
        self.keepTime = keepTime # (keep_time-1) (15 mins intervals) stock holding time
        self.dayValues = []
    
    
    def getStockValuesForDay(self):
        
        self.dayValues = []
        stockValuesFileName = 'stock_quotes/' + self.tradingDate.strftime('%d-%b-%Y') + '.xml'
        
        tree = ET.parse(stockValuesFileName)
        root = tree.getroot()
        
        indx = 0
        while True:
            try:
                self.dayValues.append(float(root[indx].text))
                indx += 1
            except:
                break
    
    
    def runTrade(self, predictionModelUsed, listOfSentiments = None):
        
        buyStocksList = [] # each entry contains a list [num of stocks bought, value at which bought, bse value, time at which bought]
        shortSellStocksList = [] # each entry contains a list [num of stocks sold, value at which sold, bse value, time at which sold]
        
        if predictionModelUsed == 'base':
            
            previousValue = self.dayValues[0]
        
        else:
            
            fileReader = open('dataset/' + self.tradingDate.strftime('%d-%b-%Y') + '/log_file.txt')
            fileReader.readline()
            l = fileReader.readline().split(' ')[0]
            fileReader.close()
            
            tree = ET.parse('dataset/' + self.tradingDate.strftime('%d-%b-%Y') + '/ann_data/' + l)
            root = tree.getroot()
            previousValue = float(root[1][0].text)
            
            predictedValuesFileName = self.tradingDate.strftime('%Y-%m-%d-d_graph.csv')
            fileReader = open('outputsRun/run1/' + predictedValuesFileName, 'r')
            fileReader.readline()
        
        i = 1
        while i < 24:
            
            if predictionModelUsed == 'base':
                
                numberOfUnits = int(self.amountInvested // self.dayValues[i])
                
                presentSentiment = listOfSentiments[i]
                if presentSentiment > 0.0:
                    buyStocksList.append([numberOfUnits, self.dayValues[i], previousValue, i])
                elif presentSentiment < 0.0:
                    shortSellStocksList.append([numberOfUnits, self.dayValues[i], previousValue, i])
                else:
                    pass
            
            elif predictionModelUsed == 'newMethod':
                
                lineValues = fileReader.readline().split(',')
                predictedValue = float(lineValues[1])
                actualValue = float(lineValues[2][:-1])
                
                change_threshold = previousValue * 0.000001
                
                numberOfUnits = int((self.amountInvested // self.dayValues[i]))
                
                if predictedValue >= (previousValue + change_threshold):
                    buyStocksList.append([numberOfUnits, self.dayValues[i], previousValue, i])
                
                elif predictedValue < (previousValue - change_threshold):
                    shortSellStocksList.append([numberOfUnits, self.dayValues[i], previousValue, i])
                
                else:
                    pass
            
            else:
                pass
            
            print buyStocksList, shortSellStocksList
            
            
            # buying stocks
            removeList = []
            for buyStock in buyStocksList:
                if (i - buyStock[3] == self.keepTime) or (previousValue >= (buyStock[2] + buyStock[2] * 0.01)):
                    self.returnValue += (buyStock[0] * (self.dayValues[i] - buyStock[1]))
                    removeList.append(buyStock)
                    print 'Stocks bought. Return value : ', self.returnValue
                else:
                    pass
            
            for item in removeList:
                buyStocksList.remove(item)
            
            # short selling stocks
            removeList = []
            for shortSellStock in shortSellStocksList:
                if (i - shortSellStock[3] == self.keepTime) or (previousValue <= (shortSellStock[2] - shortSellStock[2] * 0.01)):
                    self.returnValue += (shortSellStock[0] * (self.dayValues[i] - shortSellStock[1]))
                    removeList.append(shortSellStock)
                    print 'Stocks short-sold. Return value : ', self.returnValue
                else:
                    pass
            
            for item in removeList:
                shortSellStocksList.remove(item)
            
            if predictionModelUsed == 'newMethod':
                previousValue = actualValue
            else:
                pass
            
            i += 1
        
        if predictionModelUsed == 'newMethod':
            fileReader.close()
        else:
            pass
        
        # rest of the left stocks
        for buyStock in buyStocksList:
            self.returnValue += (buyStock[0] * (self.dayValues[i] - buyStock[1]))
            print 'Stocks bought. Return value : ', self.returnValue
        
        for shortSellStock in shortSellStocksList:
            self.returnValue += (shortSellStock[0] * (self.dayValues[i] - shortSellStock[1]))
            print 'Stocks short-sold. Return value : ', self.returnValue
