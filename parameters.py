# All parameters used in this project

#-------------------------------------------- ANN ---------------------------------------

functionType = 1 # 1 = unipolar sigmoid, 2 = bipolar sigmoid, 3 = tan hyperbolic
digitsOfSignificance = 5
lambdaValue = 0.5 # the activation function parameter
learningRate = 0.05 # learning rate
momentumValue = 0.05 # momentum factor
trainingPercent = 0.8 # percentage of data for training
validationPercent = 0.2 # percentage of data for validating
numberOfHidden = 1 # number of hidden nodes of ANN
numberOfInput = 5 # number of input nodes of ANN
numberOfOutput = 1 # number of output nodes of ANN

#------------------------------------------- Features ---------------------------------------

ourFeatureType = 3 # 3 = 2-word combinations
ourSelectionType = 2 # bns

#------------------------------------------- k-means ---------------------------------------

maximumIterations = 500 # maximum number of iterations for k-means

#------------------------------------------ Mock Trade ---------------------------------------

initialNumberOfFeatures = 300 # number of features extracted from last trading day
numberOfClusters = 7 # total_no of clusters
lastToDetermineSentiment = 3

#-------------------------------------- Projected Clustering ---------------------------------------

dimensionality = 5 # dimensionality for projected clustering
decayRate = 0.3 # decay rate of data
spreadRadiusFactor = 0.5 # the spread radius for clusters
countNewFeatures = 40 # number of features to be extracted from the new data chunk
lastFeaturesPercent = 0.6 # max percentage of features taken from previous features chunks
maximumClusters = 50 # maximum number of clusters possible

#------------------------------------- Our Trading Parameters ----------------------------------------

amountToBeInvested = 10000
keepTime = 4

#---------------------------------------- Base Paper ------------------------------------------

numberOfFeatures = 10000
baseFeatureType = 3 # 3 = 2-word combinations
baseSelectionType = 2 # 2 = bns
percentageTrainVectors = 0.8
baseInvestAmount = 10000
baseKeepTime = 4
