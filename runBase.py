# base program run

from baseWorking import HagneauImplementation

baseObject = HagneauImplementation()

print '\n1. New Training \n2. Overall Classification Results \n3. Trade \n'
choice = raw_input('Enter your choice : ')

if choice == '1':
    baseObject.extractFeatures()
    baseObject.selectFeatures()
    baseObject.getVectors()
    baseObject.trainSVM()

elif choice == '2':
    baseObject.classifyResults()

elif choice == '3':
    baseObject.doTrading()
    
else:
    pass
