#!/usr/bin/python
# -*- coding:utf-8 -*-

# define static variable


# 
import urllib2
import os, sys, re

# 时间准备
import time,datetime
Atime = time.time()
#insertTime = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(Atime))
insertTime = time.strftime('%Y-%m-%d %H:%M',time.localtime())

import MySQLdb

def db_accesscheck(db_ip,db_port,db_username,db_password,db_name):
	try:
                conn = MySQLdb.connect(host = "%s"%(db_ip) ,port=int(db_port),user = "%s"%(db_username), passwd = "%s"%(db_password), db = "%s"%(db_name))
		cur = conn.cursor()
		cur.close()
		conn.close()
		return 1
	except:
		return 0

def updateDB(db_ip,db_port,db_username,db_password,db_name):
        try:
                conn = MySQLdb.connect(host = 'db.bops.live',port=3306,user = 'ims_wr', passwd = 'xxx', db = 'jacky')
		command = '''update DBgate_Configer set db_accesscheck3 =1 where db_ip = "%s" and db_port = "%s";'''%(db_ip,db_port)
		print command
		cur = conn.cursor()
		cur.execute(command)
		conn.commit()
                cur.close()
                conn.close()
                return 1
        except:
                return 0


conn = MySQLdb.connect(host="db.bops.live",user = "ims_wr", passwd = "xxx", db = "ims", charset = "utf8")
cur = conn.cursor()
#print cur
#command = ''' insert into namenode (`clusterName`,`HeapMemoryUsedOfCommitedHeapMemory`,`ConfiguredCapacity`,`NonDFSUsed`,`DFSRemaining`,`DFSUsed`,`DFSUsedPercentage`,`DFSRemainingPercentage`,`BlockPoolUsed`,`BlockPoolUsedPercentage`,`DataNodesUsagesPercentageMin`,`DataNodesUsagesPercentageMedian`,`DataNodesUsagesPercentageMax`,`DataNodesUsagesPercentageStdev`,`LiveNodes`,`LiveNodesDecommissioned`,`DeadNodes`,`DeadNodesDecommissioned`,`DecommissioningNodes`,`insertTime`) values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'''%(clusterName,HeapMemoryUsedOfCommitedHeapMemory,ConfiguredCapacity,NonDFSUsed,DFSRemaining,DFSUsed,DFSUsedPercentage,DFSRemainingPercentage,BlockPoolUsed,BlockPoolUsedPercentage,DataNodesUsagesPercentageMin,DataNodesUsagesPercentageMedian,DataNodesUsagesPercentageMax,DataNodesUsagesPercentageStdev,LiveNodes,LiveNodesDecommissioned,DeadNodes,DeadNodesDecommissioned,DecommissioningNodes,insertTime)
#print command
#cur.execute(command)
#conn.commit()
command = ''' select db_ip, db_port, db_username, db_password, db_name from DBgate_Configer where db_accesscheck3 = 0;'''
#print command
cur.execute(command)
results = cur.fetchall()
#print results
for result in results:
	db_ip = result[0]
	db_port = result[1]
	db_username = result[2]
	db_password = result[3]
	db_name = result[4]
	print "mysql -h %s -P %s -u %s -p%s "%(db_ip,db_port,db_username,db_password)
	if ( db_accesscheck(db_ip,db_port,db_username,db_password,db_name) ):
		print "yanzheng tongguo "
		updateDB(db_ip,db_port,db_username,db_password,db_name)
	else:
		print "Some thing error!"
	#print result

