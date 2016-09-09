#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib2
import os, sys, re
import shutil

import MySQLdb

def haproxyConfigGenerate():
	conn = MySQLdb.connect(host = 'db.bops.live',port=3306,user = 'ims_wr', passwd = 'xxx', db = 'ims')
	command = '''select db_ip,db_port,db_name,db_username,db_password,dbgate_port,request_userName,request_userEmail,request_userTel from DBgate_Configer order by dbgate_port;''';
	print command
	cur = conn.cursor()
	cur.execute(command)
	results = cur.fetchall()
	if os.path.isfile("common.cfg"):
		print "配置文件存在"
		shutil.move("common.cfg","common.cfg.bak")
	# 打开文件准备写入
	fp = open("common.cfg","a")
	for result in results:
		db_ip = result[0]
		db_port = result[1]
		db_name = result[2]
		db_username = result[3]
		db_password = result[4]
		dbgate_port = result[5]
		request_userName = result[6]
		request_userEmail = result[7]
		request_userTel = result[8]
		content = ''' 
# %s %s %s %s %s %s
listen %s
        bind 0.0.0.0:%s
        mode tcp
        option  tcplog
        maxconn 4086
        server server %s:%s
'''%(request_userName,request_userEmail,request_userTel,db_ip,db_port,db_name,dbgate_port,dbgate_port,db_ip,db_port)
		fp.write(content)
	cur.close()
	conn.close()
	fp.close()

conn = MySQLdb.connect(host="db.bops.live",user = "ims_wr", passwd = "xxx", db = "ims", charset = "utf8")
cur = conn.cursor()
command = ''' select db_ip, db_port, db_username, db_password, db_name from DBgate_Configer where dbgate_port != "-";'''
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
	print result
	haproxyConfigGenerate()
	#print "mysql -h %s -P %s -u %s -p%s "%(db_ip,db_port,db_username,db_password)
	#if ( db_accesscheck(db_ip,db_port,db_username,db_password,db_name) ):
	#	print "yanzheng tongguo "
	#	updateDB(db_ip,db_port,db_username,db_password,db_name)
	#else:
	#	print "Some thing error!"
	#print result

