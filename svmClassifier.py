from PyML import SparseDataSet
from PyML.classifiers.svm import SVM
from PyML.classifiers import multi
import time
import pickle
import parameters
from featuresGet import GetFeatures
from shutil import copy

#----------------------------------------------------------------------------------------------------------------------

class SVMClassifier:
    
    def __init__(self, twoClasses):
        
        if twoClasses == True:
            self.svmObject = SVM()
        else:
            self.svmObject = multi.OneAgainstRest (SVM())
        self.trainData = None
    
    
    def prepareDataSet(self):
        
        self.trainData = SparseDataSet('data/feature_set.data', labelsColumn = 0)

    
class SVMTrain(SVMClassifier):
    
    def __init__(self, twoClasses = False):
        
        SVMClassifier.__init__(self, twoClasses)
    
    
    def prepareSVM(self):
        
        self.prepareDataSet()
    
    
    def trainingPhase(self):
        
        self.svmObject.train(self.trainData)
        
        print '\nSVM Training completed .. '
        self.svmObject.save('data/svmBase/svm_data')
        
        copy('data/feature_set.data', 'data/svmBase/feature_set.data')
        copy('data/best_features.pkl', 'data/svmBase/best_features.pkl')
    
    
class SVMResult(SVMClassifier):
    
    def __init__(self, twoClasses = False):
        
        SVMClassifier.__init__(self, twoClasses)
    
    
    def prepareSVM(self):
        
        copy('data/svmBase/feature_set.data', 'data/feature_set.data')
        self.prepareDataSet()
        
        copy('data/svmBase/svm_data', 'data/svm_data')
        self.svmObject.load('data/svm_data', self.trainData)
        
        copy('data/svmBase/best_features.pkl', 'data/best_features.pkl')
    
    
    def getResult(self, featureType):
        
        featureObject = GetFeatures('new_news')
        featureObject.extractFeatures(featureType)
        vectorNumber = featureObject.representFeatures(True)
        
        newDataVector = SparseDataSet('data/feature_set.data', labelsColumn = 0)
        results = self.svmObject.test(newDataVector)
        
        return results.confusionMatrix, results.successRate
