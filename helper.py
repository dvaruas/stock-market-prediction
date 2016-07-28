from os import listdir, walk, remove, path
from shutil import copy
import xml.etree.ElementTree as ET
from time import sleep, strftime
import pickle
import parameters
import math

#-------------------------------------------- Helper Class -------------------------------------------

class Helper:
    
    def getChiSquareValue(self, observedValue, expectedValue):
        
        chiValue = ((observedValue - expectedValue) ** 2) / expectedValue
        return chiValue
    
    
    def getZScore(self, observedValue, totalValue, mean, standardDeviation):
        
        try:
            x = (observedValue * 1.0) / totalValue
            zScore = (x - mean) / standardDeviation
        except:
            zScore = 0.0005
        
        return zScore

    
    def minMaxNormalization(self, value, maxValue, minValue, maxRange, minRange):
        
        normalizedValue = minRange + (((value - minValue) / (maxValue - minValue)) * (maxRange - minRange))
        
        return normalizedValue

    
    def zscoreNormalize(self, value, mean, standardDeviation):
        
        normalizedValue = (value - mean) / standardDeviation
        return normalizedValue
    
    
    def saveAllFeaturesExtracted(self, featureSet):
        
        allFeatures = list(set(featureSet))
        
        fileWriter = open('data/all_features.pkl', 'a')
        for feature in allFeatures:
            pickle.dump(feature, fileWriter)
        fileWriter.close()


    def fadingFunction(self, timeElapsed):
        
        return 2 ** (-parameters.decayRate * timeElapsed)
    
    
    def cleanFiles(self):
        
        numberOfCleanedFiles = 0
        
        for dirPath, dirName, dirFiles in walk('.'):
            for fileName in dirFiles:
                if fileName.endswith('~'):
                    removeFileName = path.join(dirPath, fileName)
                    remove(removeFileName)
                    numberOfCleanedFiles += 1
                else:
                    pass
        
        print 'Cleaned up .. %d files' %numberOfCleanedFiles
    
    
    def annFilesLoader(self):
        
        annFiles = listdir('ann_data')
        for fileName in annFiles:
            remove('ann_data/' + fileName)
        
        numberOfAnnFiles = 0
        dates = listdir('dataset')
        for date in dates:
            
            datePath = 'dataset/' + date + '/ann_data'
            dateFiles = listdir(datePath)
            for fileName in dateFiles:
                copy(datePath + '/' + fileName, 'ann_data/' + fileName)
                numberOfAnnFiles += 1
        
        print 'Copied .. %d files' %numberOfAnnFiles
    
    
    def activationFunction(self, value):
        
        # sigmoid fnction, range = [0, 1]
        if parameters.functionType == 1:
            outputValue = 1.0 / (1.0 + math.exp(parameters.lambdaValue * (-value)))
        
        # bipolar sigmoid function, range = [-1, 1]
        elif parameters.functionType == 2:
            outputValue = (2.0 / (1 + math.exp(parameters.lambdaValue * (-value)))) - 1.0
        
        # tan hyperbolic, range = [-1, 1]
        elif parameters.functionType == 3:
            a = math.exp(parameters.lambdaValue * value)
            b = math.exp(parameters.lambdaValue * (-value))
            outputValue = (a - b) / (a + b)
        
        else:
            pass
        
        return outputValue
    
    
    
    def cleanBeforeTrade(self):
        
        filesInLastDir = listdir('last')
        filesInNewDir = listdir('new_news')
        
        for fileName in filesInLastDir:
            remove('last/' + fileName)
        
        for fileName in filesInNewDir:
            remove('new_news/' + fileName)
        
        try:
            remove('data/all_best_features.pkl')
            remove('data/all_features.pkl')
            remove('data/cluster_info.pkl')
            remove('data/feature_set.data')
            remove('data/last_bst_features.pkl')
        except:
            pass
    
    
    def corpusFilesLoader(self, onlyTwoClasses = False):
        
        corpusFiles = listdir('corpora')
        for fileName in corpusFiles:
            remove('corpora/' + fileName)
        
        numberOfFilesCopied = 0
        
        dates = listdir('dataset')
        for date in dates:    
            corporaPath = 'dataset/' + date + '/corpora'
            corporaFiles = listdir(corporaPath)
            
            for fileName in corporaFiles:
                if onlyTwoClasses == False:
                    copy(corporaPath + '/' + fileName, 'corpora/' + fileName)
                
                else:
                    tree = ET.parse(corporaPath + '/' + fileName)
                    root = tree.getroot()
                    
                    for sentimentNode in root.iter('sentiment'):
                        
                        if sentimentNode.text == 'neutral':
                            sentimentNode.text = 'positive'
                        
                        else:
                            pass
                    
                    tree.write('corpora/' + fileName)
                
                numberOfFilesCopied += 1
        
        print 'Copied .. %d files' %numberOfFilesCopied
