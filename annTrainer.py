# training for the ann

from ann import AnnTrain
from helper import Helper

helperObject = Helper()
helperObject.annFilesLoader()

annObject = AnnTrain()
annObject.prepareTrainingData('ann_data')
annObject.trainTheAnn()
