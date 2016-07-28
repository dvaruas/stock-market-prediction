# Stock Price prediction model

from kmeans import run_kmeans
from ann_run import calculate_output
from scraping import web_scraper
from proj_clustering import p_clustering
from ann import Ann
import parameters
from time import sleep
import pickle

#------------------------------------------ Parameters ------------------------------------------

parameters.no_of_clusters = 37
parameters.dimensionality = 4500
parameters.no_of_hidden = 2

#------------------------------------------ Prediction Model Class ------------------------------------------

class pmodel:

	def __init(self):
		# store clustering model info
		self.cluster_info = []


	
	def initial_model(self):
	
		newly_trained = False
		
		print "\n..Initial Training : 1. Continue with last initial cluster, 2. New training"
		ch = raw_input('..Enter your choice : ')
		if ch == 1:
			f_cluster = open('data/cluster_info.pkl', 'r')
			self.cluster_info = pickle.load(f_cluster)
			f_cluster.close()
	
		elif ch == 2:
			# form clusters from the data in the last folder ..
			obj = GetFeatures('last')
			obj.feature_extraction(3)
			obj.feature_selection(2, 4500)
			obj.feature_representation()
			
			run_kmeans(parameters.no_of_clusters)
			f_cluster = open('data/cluster_info.pkl', 'r')
			self.cluster_info = pickle.load(f_cluster)
			f_cluster.close()
			
			newly_trained = True
			
		else:
			print '..Wrong choice'

		return newly_trained
			
	def real_time_handle(self, projc_obj, time, ann_obj):

		start_time = datetime.now() # current time
		obj = web_scraper(start_time)
		
		# get the sensex, oil, exchange values
		sensex_bfr15 = obj.sensex_val()
		xchng_bfr15 = obj.exchange_rate()
		oil_bfr15 = obj.oil_price()

		print "\n .. 15 minutes to collect news .. "
		# wait for 15 minutes
		
		# get sensex, oil, exchange values
		sensex_curr = obj.sensex_val()
		xchng_curr = obj.exchange_rate()
		oil_curr = obj.oil_price()
		
		f_name = strftime('%j%m%y%H%M%S') + '.xml'  # day month year hour minute second
		obj.news_scrap(f_name)
		print "\n .. News data collected .. "
		
		senti = projc_obj.process_stream(time)
		print "\n .. News Data classified .. "
		
		inputs = [0, 0, 0, 0]
		inputs[0] = (sensex_curr - sensex_bfr15)
		inputs[1] = (xchng_curr - xchng_bfr15)
		inputs[2] = (oil_curr - oil_bfr15)
		inputs[3] = senti
		
		# ann predicted value
		predicted_val = calculate_output(ann_obj, inputs)
		
		print '\n.. Current BSE Index value :', sensex_curr
		print '\n.. Predicted BSE Index value after 15 minutes :', predicted_val[0]
		
		sleep(300) 
		bse_aftr5 = obj.sensex_val()
		sleep(300)
		bse_aftr10 = obj.sensex_val()
		sleep(300)
		bse_aftr15 = obj.sensex_val()
		
		# sentiment according to change, threshold 5 .. 
		change = (bse_aftr5 - bse_time0)*0.5 + (bse_aftr10 - bse_aftr5)*0.3 + (bse_aftr15 - bse_aftr10)*0.2
		if change < 0.0:
			sentiment = 'negative'
		else:
			if change >= 5.0:
				sentiment = 'positive'
			else:
				sentiment = 'neutral'
		
		print '\n.. Actual BSE Index value :', bse_aftr15
		
		projc_obj.prepare_for_next(sentiment, f_name)

#------------------------------------------ The Mains ------------------------------------------

def mains():
	# for ann - load the path weights ..
	file_r = open('data/min_error_weights.pkl' , 'r')
	ann_weights = pickle.load(file_r)
	file_r.close()

	hidden_weights = ann_weights[0]
	output_weights = ann_weights[1]
	
	ann_obj = Ann(1, parameters.no_of_hidden, 4)
	
	i = 0
	for hnode in ann_obj.hidden_nodes:
		j = 0
		for w in hnode.weights:
			hnode.weights[j] = hidden_weights[i]
			i += 1
			j += 1
	i = 0
	for onode in ann_obj.output_nodes:
		j = 0
		for w in onode.weights:
			onode.weights[j] = output_weights[i]
			i += 1
			j += 1
	
	# prediction model starts .. 
	obj = pmodel()
	obj_p = p_clustering(parameters.no_of_clusters, parameters.dimensionality)

	time = 3

	train_status = obj.initial_model()
	print "\n..Clusters trained. Real Time handling of data started"
	obj_p.prepare_fclusters(obj.cluster_info, time)

	ch = 'y'
	while ch == 'y':
		obj.real_time_handle(obj_p, time, ann_obj, train_status)
		ch = raw_input("\n..Want to continue ? (y/n) : ")
		time += 1
		train_status = False
	
	print '\n..Exiting'
	
#------------------------------------------ Program Run ------------------------------------------

mains()
