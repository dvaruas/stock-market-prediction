# The offline data collection program


import datetime
import xml.etree.ElementTree as ET
from os import remove
from scraping import WebScraper
from processing import PreProcessor

#--------------------------------------------- Helper Functions ------------------------------------------

# pre-processing of the news files is done
def pre_processing(file_name):	
	obj = PreProcessor()
	obj.processing(file_name)
	
# puts the sentiment values in the news
def modify_news_xml(file_name, sentiment):

	tree = ET.parse(file_name)
	root = tree.getroot()	
	for senti in root.iter('sentiment'):
		senti.text = sentiment
		
	tree.write('others/' + file_name)
	remove(file_name)
	

# values for children of a given parent put from a dictionary
def define_children(parent, given_dict):
	bse = ET.SubElement(parent, "bse")
	bse.text = str(given_dict['bse'])
	
	xchng = ET.SubElement(parent, "exchange")
	xchng.text = str(given_dict['exchange'])
		
	oil = ET.SubElement(parent, "oil")
	oil.text = str(given_dict['oil'])
	
	gold = ET.SubElement(parent, "gold")
	gold.text = str(given_dict['gold'])

		
# save the rates in an xml file	
def save_rates_data(file_name, init_dict, later_dict, sentiment, bse_val15):
	new_root = ET.Element("values")	
	value1 = ET.SubElement(new_root, "before15")
	define_children(value1, init_dict)
	
	value2 = ET.SubElement(new_root, "current")
	define_children(value2, later_dict)
	
	value3 = ET.SubElement(new_root, "sentiment")
	value3.text = sentiment
	
	value4 = ET.SubElement(new_root, "after15")
	value4.text = str(bse_val15)
		
	tree = ET.ElementTree(new_root)
	tree.write('others/ann_' + file_name)
	
#--------------------------------------------- The Offline Collector ------------------------------------------

t = raw_input("Enter time(h:m) : ")
t_list = t.split(':')

hour = int(t_list[0])
minute = int(t_list[1])

start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(hour, minute))
end_time = start_time + datetime.timedelta(minutes = 15)

ch = 'y'
i = 0
prev_count = None
prev_f_name = None
while ch != 'n':
	
	obj = WebScraper(start_time, end_time)
	f_name = datetime.date.today().strftime('%d-%m-%y-') + end_time.strftime('%H:%M:%S') + '.xml'
	count = obj.getNews(f_name, True)
	
	print "News collected :", count
	
	f_w = open('others/log_file.txt', 'a') # log file
	f_w.write(f_name + ' ' + str(count) + ' ' + '\n')
	f_w.close()
	
	if count > 0:
		pre_processing(f_name)
	else:
		pass
	
	if i == 0:
		print "\nstart time data : "
		timer = start_time
		
		s_val = float(raw_input(timer.strftime('%H:%M') + ' sensex value : '))
		o_val = float(raw_input(timer.strftime('%H:%M') + ' oil price : '))
		e_val = float(raw_input(timer.strftime('%H:%M') + ' exchange rate : '))
		g_val = float(raw_input(timer.strftime('%H:%M') + ' gold value : '))
		val_dict_prev = {'bse' : s_val, 'exchange' : e_val , 'oil' : o_val, 'gold' : g_val}
	
	s_val = val_dict_prev['bse']
	
	print '\n'
	timer = start_time
	timer += datetime.timedelta(minutes = 5)
	s_val1 = float(raw_input(timer.strftime('%H:%M') + ' sensex value : '))
	
	timer += datetime.timedelta(minutes = 5)
	s_val2 = float(raw_input(timer.strftime('%H:%M') + ' sensex value : '))
	
	# the current data
	print "\nCurrent data : "
	timer = end_time
	s_val = float(raw_input(timer.strftime('%H:%M') + ' sensex value : '))
	o_val = float(raw_input(timer.strftime('%H:%M') + ' oil price : '))
	e_val = float(raw_input(timer.strftime('%H:%M') + ' exchange rate : '))
	g_val = float(raw_input(timer.strftime('%H:%M') + ' gold value : '))
	val_dict_now = {'bse' : s_val, 'exchange' : e_val , 'oil' : o_val, 'gold' : g_val}
	
	s_val3 = val_dict_now['bse']
	print "\nChange in 0 - 5 minutes :", str(s_val1 - s_val)
	print "Change in 5 - 10 minutes :", str(s_val2 - s_val1)
	print "Change in 10 - 15 minutes :", str(s_val3 - s_val2)
	
	change = (s_val1 - s_val)*0.5 + (s_val2 - s_val1)*0.3 + (s_val3 - s_val2)*0.2

	# find sentiment according to market analysis, 5 threshold
	if change < 0.0:
		sentiment = 'negative'
	else:
		if change >= 5.0:
			sentiment = 'positive'
		else:
			sentiment = 'neutral'
			
	start_time = end_time
	end_time = start_time + datetime.timedelta(minutes = 15)
	
	if i != 0:
		if prev_count > 0:	
			modify_news_xml(prev_f_name, sentiment)
		save_rates_data(f_name, val_dict_prev2, val_dict_prev, sentiment, s_val)
	else:
		print '\nsentiment : ', sentiment
		
	val_dict_prev2 = dict(val_dict_prev)
	val_dict_prev = dict(val_dict_now)
	i += 1
	prev_f_name = f_name
	prev_count = count
	
	ch = raw_input('continue? (y/n) : ')
