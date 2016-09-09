#!/usr/bin/python
#coding:utf8
# -*- coding:utf-8 -*-

import urllib2
import os, sys, re
import shutil
import MySQLdb
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

def getMaxdbgatePort():
	try:
		conn = MySQLdb.connect(host = 'db.bops.live',port=3306,user = 'ims_wr', passwd = 'xxx', db = 'ims')
		command = '''select max(dbgate_port) from DBgate_Configer;'''
		cur = conn.cursor()
		cur.execute(command)
		results = cur.fetchall()
		if len(results) == 1:
			if results[0][0] >= 8500 :
				cur.close()
				conn.close()
				return results[0][0]
			else:
				print "dbgate_中国port有问题"
		else:
			print "查询结果有问题"
	except:
		return 0

def updatedbgatePortDB(db_ip,db_port,dbgate_port):
        try:
                conn = MySQLdb.connect(host = 'db.bops.live',port=3306,user = 'ims_wr', passwd = 'xxx', db = 'ims')
		command = '''update DBgate_Configer set dbgate_port="%s" where db_ip = "%s" and db_port = "%s";'''%(dbgate_port,db_ip,db_port)
		print command
		cur = conn.cursor()
		cur.execute(command)
		conn.commit()
                cur.close()
                conn.close()
                return 1
        except:
                return 0

def haproxyConfigGenerate():
	conn = MySQLdb.connect(host = 'db.bops.live',port=3306,user = 'ims_wr', passwd = 'xxx', db = 'ims')
	command = '''select db_ip,db_port,db_name,db_username,db_password,dbgate_port,request_userName,request_userEmail,request_userTel from DBgate_Configer where dbgate_port != "-";''';
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

def alertRequestUser(info):
	print urllib2.urlopen('http://mailapi.vxlan.net/mail.php?%s'%info, timeout=10)


conn = MySQLdb.connect(host="db.bops.live",user = "ims_wr", passwd = "xxx", db = "ims", charset = "utf8")
cur = conn.cursor()
command = ''' select db_ip, db_port, db_username, db_password, db_name,request_userEmail,request_userGroup,request_userName from DBgate_Configer where db_accesscheck1 = 1 and db_accesscheck2 = 1 and db_accesscheck3 = 1 and db_accesscheck4 = 1 and dbgate_port = "-" order by dbgate_port;'''
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
	request_userEmail = result[5]
	request_userGroup = result[6]
	request_userName = result[7]
	print result
	dbgate_port = int(getMaxdbgatePort()) + 1
	print dbgate_port
	if updatedbgatePortDB(db_ip,db_port,dbgate_port):
		print "开始进行配置更新"
		haproxyConfigGenerate()
		sendto="%s"%(request_userEmail)
		subject="[dbgate申请-中国] %s %s %s %s"%(db_ip,db_port,request_userGroup,request_userName)
		content="您好，您申请的dbgate中国 已经开通，使用方法是 mysql -h dbgate.bigdata.le.com -P %s -u %s -p"%(dbgate_port,db_username)
		info="sendto=%s&subject=%s&body=%s"%(sendto,subject,content)
		alertRequestUser(info)
	#print "mysql -h %s -P %s -u %s -p%s "%(db_ip,db_port,db_username,db_password)
	#if ( db_accesscheck(db_ip,db_port,db_username,db_password,db_name) ):
	#	print "yanzheng tongguo "
	#	updateDB(db_ip,db_port,db_username,db_password,db_name)
	#else:
	#	print "Some thing error!"
	#print result

