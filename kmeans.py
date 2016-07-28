# Full Dimensional k means 

from random import sample
import pickle
import time
from threading import Thread
from Queue import Queue
import parameters

#-------------------------------------------- Cluster Class ---------------------------------------

class Cluster:
	
	def __init__(self, point):
		
		self.centroid = point
		self.pointsInCluster = []
	
#-------------------------------------------- KMeans Class ---------------------------------------

class KMeans:

	def __init__(self):
		
		self.numberOfClusters = parameters.numberOfClusters
		self.points = None
		self.sentiments = None
		self.clusters = []
		self.previousSum = 0.0 # sum of all centroids of clusters
		self.numberOfDimensions = None


	def getDataPoints(self):
		
		self.points = []
		self.sentiments = []
		
		fileReader = open('data/feature_set.data', 'r')
		for line in fileReader:
			values = line.split(',')
			self.sentiments.append(values.pop(0))
			weights = [float(w) for w in values]
			self.points.append(weights)
		fileReader.close()
		
		self.numberOfDimensions = len(self.points[0]) # number of dimensions

	
	def distance(self, pointOne, pointTwo):
		
		# Calculater the distance using the Manhattan Segmental Distance
		distance = sum([abs(pointOne[i] - pointTwo[i]) for i in range(self.numberOfDimensions)]) / self.numberOfDimensions
		
		return distance


	def getInitialCenters(self):
		
		# Performs a greedy search to get good initial starting centroids
		
		randomPointsIndex = sample(range(len(self.points)), 2 * self.numberOfClusters)
		initialCentres = sample(randomPointsIndex, 1)
		otherPoints = [point for point in randomPointsIndex if point not in initialCentres]
		distance = {}
		
		for pointIndex in otherPoints:
			distance[pointIndex] = self.distance(self.points[pointIndex], self.points[initialCentres[0]])
		
		i = 1
		while i < self.numberOfClusters:
			
			newCenter = [key for (key, value) in distance.items() if value == max(distance.values())][0]
			initialCentres.append(newCenter)
			otherPoints.remove(newCenter)
			del distance[newCenter]
			
			for pointIndex in otherPoints:
				distance[pointIndex] = min(distance[pointIndex], self.distance(self.points[pointIndex], self.points[newCenter]))
			i += 1 
			
		for centerPoint in initialCentres:
			clusterObject = Cluster(self.points[centerPoint])
			clusterObject.pointsInCluster.append(centerPoint)
			self.clusters.append(clusterObject)
		
		print '\n..Initial Cluster centroids formed'
		print initialCentres
	
	
	def assignToCluster(self):
		
		# Assigning of the points to clusters according to the distance from each cluster centroid
		for clusterObject in self.clusters:
			clusterObject.pointsInCluster = []
		
		clusterIndex = 0
		for point in self.points:
			distance = float('inf')
			index = 0
			selectedCluster = -1
			while index < self.numberOfClusters:
				distancePointToCluster = self.distance(point, self.clusters[index].centroid)
				
				if distancePointToCluster < distance:
					distance = distancePointToCluster
					selectedCluster = index
				else:
					pass
				
				index += 1
			
			self.clusters[selectedCluster].pointsInCluster.append(clusterIndex)
			clusterIndex += 1


	def parallelWork(self, clusterObject, clusterSumQueue):
		
		i = 0
		clusterCenter = [0.0] * self.numberOfDimensions
		
		if len(clusterObject.pointsInCluster) > 0:
			while i < self.numberOfDimensions:
				clusterCenter[i] = (sum([self.points[x][i] for x in clusterObject.pointsInCluster]) / len(clusterObject.pointsInCluster))
				i += 1
		clusterObject.centroid = list(clusterCenter)
		clusterSum = sum(clusterObject.centroid)
		clusterSumQueue.put(clusterSum)


	def recalculateCentroids(self):
		
		# Replacing the cluster centroid by the mean of all points in the cluster
		currentSum = []
		for i in range(self.numberOfClusters):
			currentSum.append(Queue())
		
		threads = []
		i = 0
		
		for clusterObject in self.clusters:
			thread = Thread(self.parallelWork(clusterObject, currentSum[i]))
			threads.append(thread)
			thread.start()
			i += 1
		
		for thread in threads:
			thread.join()
			
		currentSumList = [currentSum[i].get() for i in range(self.numberOfClusters)]
		totalCurrentSum = sum(currentSumList)
		
		if totalCurrentSum == self.previousSum:
			flag = False
		else:
			flag = True
			
		self.previousSum = totalCurrentSum
		
		return flag


	def saveClusters(self):
		
		clustersPoints = []
		
		for clusterObject in self.clusters:
			if len(clusterObject.pointsInCluster) > 0:
				clustersPoints.append(clusterObject.pointsInCluster)
			else:
				pass
		
		fileWriter = open('data/cluster_info.pkl', 'w')
		pickle.dump(clustersPoints, fileWriter)
		fileWriter.close()
		
		print '\n.. Cluster information saved ..'
