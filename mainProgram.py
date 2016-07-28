# main program for functionalities

import datetime
import parameters
from predictionModel import PredictionModel
from tradingEngine import TradingEngine
from helper import Helper

#---------------------------------------------------------------------------------------------------------------

class Main:
    
    def __init__(self):
        
        self.dateOfTrade = None
        self.mockPredictionObject = None
        self.mockTradingObject = None
        self.helperObject = Helper()
    
    
    def getDate(self):
        
        dateEntered = raw_input('\nEnter date (dd-mm-yyyy) : ')
        dateList = dateEntered.split('-')
        dateList = [int(dateElement) for dateElement in dateList]
        self.dateOfTrade = datetime.date(dateList[2], dateList[1], dateList[0])
    
    
    def main(self):
        
        print '\n1. Prediction \n2. Trading \n'
        choice = raw_input('Enter your choice : ')
        
        self.getDate()
        
        if choice == '1':
            self.helperObject.cleanBeforeTrade()
            
            self.mockPredictionObject = PredictionModel(self.dateOfTrade)
            
            self.mockPredictionObject.preConfigureModel()
            
            goToTrade = raw_input('\n..Go to trading? (y/n): ')
            
            if goToTrade == 'y':
                runAllAtOnce = raw_input('\n..Run all at once? (y/n): ')
                self.mockPredictionObject.tradeRun(runAllAtOnce)
            
            else:
                print 'Process aborted by user ..'
        
        elif choice == '2':
            
            self.mockTradingObject = TradingEngine(self.dateOfTrade, parameters.amountToBeInvested, parameters.keepTime)
            
            self.mockTradingObject.getStockValuesForDay()
            self.mockTradingObject.runTrade('newMethod')
            
            print 'Return Value for trade :', self.mockTradingObject.returnValue
        
        else:
            pass
