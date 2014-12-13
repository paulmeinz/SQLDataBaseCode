import csv
import numpy
import pdb
import sqlite3
import os

### Functions for uploading dotprobe data to the dotprobe table in the dotprobe database. Also includes functions for cleaning the data of outliers and trials with incorrect responses ###
def workingDR():
	'''
	Function for checking files included in the dotprobe database with new files in datafolder
	'''

	filesinfolder = []
	txtfilesinfolder = []
	filesindb = []	
	Notincluded = []	


	#For each file in the os list, append the file name to a list
	for file in os.listdir('.'):
		filesinfolder.append(file)

	#Only include in file name list if the file ends in .txt
		
	for name in filesinfolder:
		
		if name[-4:] == '.txt':
	
			if len(name) == 8:
				txtfilesinfolder.append(name[0:4])
				
			if len(name) == 9:	
				txtfilesinfolder.append(name[0:5])
				
			

	conn = sqlite3.connect('dotprobe.db')
	c = conn.cursor()

	for row in c.execute('select distinct(id) from dotprobe'):
		filesindb.append(str(row[0]))

	#Compare the two lists
	Diff = list(set(txtfilesinfolder) - set(filesindb))

	#Add .txt to the end of each file that is not included in the txt database
	for name in Diff:
		Notincluded.append(name)
	print len(Notincluded)

	return Notincluded


def preload_data():
	"""
	Function for reading all the tab delimited .txt files in a folder into python.
	
	:return: A dictionary with data from each tab file as an entry
	"""
	
	# Open all .txt files in a folder in Python
	txt_files = workingDR()
	tempdata = []
	data_dict = {}
	
	# Open each .txt file with csv.reader.
	for data_file in txt_files:
		reader = csv.reader(open(data_file + '.txt', 'rb'), delimiter='\t')
		
		# Append each row in the .txt file to a list. Then return the list.
		for row in reader:
			tempdata.append(row)
		
		tempdata[0:1] = []

		data_dict[data_file] = tempdata

		tempdata = []
		
		print "%s Pre-Loaded" % data_file[0:5]
	print data_dict.viewkeys		
	return data_dict


def cleandata_updatedb(data_dict, name):
	"""
	A function for removing outliers/incorrect responses and practice trials from each participants data using the 
	dictionary yielded in the separate_data() function.
	
	It then takes each participant's data and committs it to an SQL database, where it is stored
	for later use.
	
	:param data_dict: The dictionary yielded from the separate_data() function.

	:param name: The ID of a participant that references an entry in the aforementioned dictionary.
	"""
	conn = sqlite3.connect('dotprobe.db')
	c = conn.cursor()

	tempdata = []
	tempdata2= []
		
	# The location of these columns has to be found for each participant because the mom and child data have slightly 		
	# different column numbers.		
		
	pairtype = 0
	stiml = 0
	stimr = 0
	trialtype = 0
	response = 0
	correct = 0
	reactiontime = 0
	duration = 0

	# Search through the first row to find the position of each column entitled with the names outlined below.
		
	for position in range(len(data_dict[name][0])):
		if data_dict[name][0][position] == 'pairtype':
			pairtype = position
		elif data_dict[name][0][position] == 'stimL':
			stiml = position
		elif data_dict[name][0][position] == 'stimR':
			stimr = position
		elif data_dict[name][0][position] == 'trialtype':
			trialtype = position
		elif data_dict[name][0][position] == 'probe.RESP':
			response = position
		elif data_dict[name][0][position] == 'correct':
			correct = position
		elif data_dict[name][0][position] == 'probe.RT':
			reactiontime = position
		elif data_dict[name][0][position] == 'duration':
			duration = position

	for row in data_dict[name]:			
		tempdata.append([name[0:5],row[stiml],row[stimr],row[pairtype],row[trialtype],row[response],row[correct],row[duration],row[reactiontime]])
		


	tempdata[0:12] = []		
	
	# For each row in the partcipants data (assigned to tempdata), assigned the 8th element (reaction time) to a temporary
	# list - dataclean
	
	for row in tempdata:
		tempdata2.append(numpy.float(row[8]))
		
	sd = numpy.std(tempdata2)
	mean = numpy.mean(tempdata2)
	tempdata2 = []
		
	# For each row in a participant's data. If the participants response was correct (5rd element = 6th element)
	# and their reaction time response (8th element) is not 3 standard deviations or more above their average reaction time.
	# append the row to a temporary dataset.
	
	for row in tempdata:
		if row[5] == row[6] and numpy.float(row[8]) < 2000 and (numpy.float(row[8])-mean)/sd < 3.0:
			tempdata2.append(row)
	
	tempdata = []
	
	# For each row in a participants data (now assigned to tempdate2, determin where the dot and picture were located, then assign
	# participants id, trialtype (or picturetype), duration of trial, picture location, dot location, and rt to a new list of lists.

	for row in tempdata2:
		if row[4] == 'congruent' and row[6] == 'q':
			tempdata.append([row[0], row[1], row[2], row[3], row[7], 'left', 'left', row[8]])
		elif row[4] == 'congruent' and row[6] == 'p':
			tempdata.append([row[0], row[1], row[2], row[3], row[7], 'right', 'right', row[8]])
		elif row[4] == 'incongruent' and row[6] == 'q':
			tempdata.append([row[0], row[1], row[2], row[3], row[7], 'right', 'left', row[8]])
		elif row[2] == 'incongruent' and row[6] == 'p':
			tempdata.append([row[0], row[1], row[2], row[3], row[7], 'left', 'right', row[8]])
	# For each row in the temporary dataset, if row[3] equals 'happy-neutral', replace it with 'hap-neutral'
	
	for row in tempdata:
		if row[3] == 'happy-neutral':
			row[3:4] = ['hap-neutral']
				
	c.executemany('insert into updatetab values (NULL,?,?,?,?,?,?,?,?)', tempdata)	
	c.executemany('insert into dotprobe values (NULL,?,?,?,?,?,?,?,?)', tempdata)

	print 'participant %s entered to updatetab and dotprobe table' % tempdata[0][0] 	
	
	tempdata = []
	dataclean = []
	conn.commit()				

### Functions for creating subtables in the dotprobe database used in data analysis ###

	
def biasscores():
	"""
	Updates the bias score table for the primary analysis
	"""
		
	conn = sqlite3.connect('dotprobe.db')
	c = conn.cursor()

	duration = [200,1250]
	pairtype = ["'hap-neutral'", "'cry-neutral'","'baby-neutral'"]	

	#Create a view for congruent trials (e.g., where face and dot appear same place)

	c.execute("create view congruent as select id, duration, pairtype, avg(rt) as 'rt' from updatetab where (picloc = 'left' and dotloc = 'left') or (picloc = 'right' and dotloc = 'right') group by id, duration, pairtype")

	#Create a view for incongruent trials

	c.execute("create view incongruent as select id, duration, pairtype, avg(rt) as 'rt' from updatetab where (picloc = 'right' and dotloc = 'left') or (picloc = 'left' and dotloc = 'right') group by id, duration, pairtype")

	#Subtract bias scores and enter data into cbias

	c.execute('insert into cbias select NULL, congruent.id, congruent.duration, congruent.pairtype, congruent.rt - incongruent.rt from congruent left join incongruent on congruent.id = incongruent.id and congruent.duration = incongruent.duration and congruent.pairtype = incongruent.pairtype') 
	
	for row in c.execute('select distinct(id) from congruent'):
		print '%d added to bias table' % row[0]

	c.execute('drop view congruent')
	c.execute('drop view incongruent')
	c.execute('delete from updatetab')

	
	conn.commit()
	conn.close()	

### Functions for uploading classification keys to database for join functions at a later time ###

def uploadclassificationkeys():
	'''

	Function for uploading the classification keys to tables in the dot-probe database


	:param create: If true it creates, new tables for the classification keys

	NOTE: There is no update function for this function because the data were collected years ago
	and no new data will be added after the initial upload

	'''
	conn = sqlite3.connect('dotprobe.db')
	c = conn.cursor()	
	
	ssplist = []

	with open ('SSP.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			ssplist.append(row)

	ssplist[0:1] = []

	c.executemany('insert into ssp values(NULL,?,?,?)', ssplist)

	print 'SSP key uploaded to database'

	conn.commit()
	conn.close()
	  	
		
