#! /usr/bin/python

import sqlite3

### Functions for creating data tables necessary for analysis of dissertation data

def createtables():
	conn = sqlite3.connect('dotprobe.db')
	c = conn.cursor()
	
	# Update Table for newly collected data
	c.execute('''create table updatetab(		
		x integer primary key autoincrement,
		id integer,
		stiml varchar,
		stimr varchar,
		pairtype varchar,
		duration integer,
		picloc varchar,
		dotloc varchar,
		rt float)''')

	# Main Table
	c.execute('''create table dotprobe(		
		x integer primary key autoincrement,
		id integer,
		stiml varchar,
		stimr varchar,
		pairtype varchar,
		duration integer,
		picloc varchar,
		dotloc varchar,
		rt float)''')
	
	# Bias Score Subtable
	c.execute('''create table cbias(
		x integer primary key autoincrement,		
		id int,
		duration int,
		pairtype var char,
		bias float)''')


	# Classification key table
	c.execute('''create table ssp(
		x integer primary key autoincrement,
		id int,
		class int,
		subclass int)''')

	
createtables()
