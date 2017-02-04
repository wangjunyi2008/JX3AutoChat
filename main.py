# -*- coding:gbk -*- 
#2017/2/1

#Potential bugs:
#HM interface may build up a new table to log, remaining the old table as backup, which may cause the malfunction of this version 

import sqlite3
import time
import datetime
import re
from send.sendcore import *
from core.debug import *
import tempfile
import random

import core.settings
import core.game
import core.jx3tieba
import os.path
import os
import shutil

#dbname = "chat_log.db"
dbname = "D:\\Game\\JX3\\bin\\zhcn\\interface\\MY\\@DATA\\252201579137825167@zhcn\\userdata\\chat_log.db" #����Ѱ����
dbname = "D:\\Game\\JX3\\bin\\zhcn\\interface\\MY\\@DATA\\252201579140638668@zhcn\\userdata\\chat_log.db" #���ݹ�Բ�߳�
dbname = "D:\\Game\\JX3\\bin\\zhcn\\interface\\MY\\@DATA\\252201579137405962@zhcn\\userdata\\chat_log.db" #ȫ�������
tempdir = tempfile.mkdtemp()

MAX_CHATCOUNT_IN_INTERVAL = 10

def database_query(query_str):
	try:
		conn = sqlite3.connect(dbname)
		retstr = conn.execute(query_str).fetchall()
	except Exception as err:
		debug("***database_query error: " +str(err)+", ʹ�ô��淽ʽ",1)
		filename = str(random.randint(0,99999999))
		shutil.copyfile(dbname,tempdir+"\\"+filename)
		connnew = sqlite3.connect(dbname,tempdir+"\\"+filename)
		retstr = connnew.execute(query_str).fetchall()
		os.remove(tempdir+"\\"+filename)
	return retstr


def init_rewritetime():
	f = open("starttime.txt",'rU')
	s = f.readline()
	f.close()
	s = str(int(s)+1)
	f = open("starttime.txt",'w')
	f.write(s)
	f.close()
	return s

def GetTables():
	dbtables = []
	s = database_query("select name from sqlite_master where type = 'table' order by name;")
	for table in s:
		dbtables.append(table[0])
	debug("GetTables Return---->"+str(dbtables),3)
	return  dbtables
	
def GetNewestPrivateChat(dbtable,numforchats):
	ret = database_query("SELECT TIME,TALKER,MSG FROM "+dbtable+" WHERE CHANNEL = 1 ORDER BY TIME DESC LIMIT 0,"+str(numforchats))
	return ret
		
	

def GetMessageLine(strrawmsg):
	p = re.compile('text="(.*?)"')
	s = " ".join(p.findall(strrawmsg))
	try:
		mhint = s.find("��")
		s = s[mhint+2:]
	except:
		pass
	debug("GetMessageLine---->"+s,3)
	return s

def RealTimeGetMSG(dbtables,lastmsg):
	newlastmsg = {}
	for table in dbtables:
		msg = GetNewestPrivateChat(table,MAX_CHATCOUNT_IN_INTERVAL)
		newlastmsg[table] = str(msg[0][0])+"--"+str(msg[0][1])+"--"+str(msg[0][2])
		for (rettime,rettalker,retmsg) in msg:
			
			if (lastmsg[table]==str(rettime)+"--"+rettalker+"--"+retmsg)or(lastmsg[table]==""):
				break #considering orderd by time, if encounter equals, the messages after are old.
			if retmsg.find("�����ĵض�")<0: # avoid the response interrupting 
				debug(str(rettime)+"###"+str(rettalker)+"###"+str(GetMessageLine(retmsg)),2)
				
				core.game.core_input(rettalker,rettime,str(GetMessageLine(retmsg)))
				
	return newlastmsg
			
def RealTimeUpdateTieba(): #δ����
	timehm = time.strftime("%H-%M")
	todayymd = time.strftime("%y-%m-%d")
	if timehm==core.settings.get_value("TIEBA_UPDATETIME"):
		if core.settings.get_value("TIEBA_UPDATE_TO") != todayymd:
			debug("REALTIME_TIEBA_UPDATE : START",1)
			core.jx3tieba.tiebatop_update("������",todayymd)
			core.settings.set_value('TIEBA_UPDATE_TO',todayymd)
			time.sleep(1)
			try:
				f = open(todayymd+"_2",'rU',encoding = 'utf-8')
				tmplist = []
				for i in range(0,10):
					tmplist.append(f.readline().strip("\n"))
				core.settings.set_value('TIEBA_SHIDA',tmplist)
				core.settings.set_value('TIEBA_SHIDA_UPDATE',todayymd)
			except:
				debug("******REALTIME_TIEBA_UPDATE : ERROR",1)

def InitUpdateTieba():
	debug("��ʼ������ʮ�� ����",2)
	todayymd = time.strftime("%y-%m-%d")
	if not os.path.exists(todayymd+"_2"):
		debug("δ��⵽����ʮ��")
		core.jx3tieba.tiebatop_update("������",todayymd)
		time.sleep(1)
	else:
		debug("��⵽����ʮ��ֱ��ʹ���������ļ�")	
	f = open(todayymd+"_2",'rU',encoding = 'utf-8')
	tmplist = []
	for i in range(0,10):
		tmplist.append(f.readline().strip("\n"))
	core.settings.set_value('TIEBA_SHIDA',tmplist)
	core.settings.set_value('TIEBA_SHIDA_UPDATE',todayymd)
	core.settings.set_value('TIEBA_UPDATE_TO',todayymd)
	


core.settings.set_value('RESTARTTIME',init_rewritetime())
InitUpdateTieba()
dbtables = GetTables()
dbtables.remove("ChatLogIndex")
dbtables.remove("ChatLogInfo")
lastmsg = {}
for table in dbtables:
	lastmsg[table] = ""
while (1):
	lastmsg = RealTimeGetMSG(dbtables,lastmsg)
	time.sleep(0.2)
fd.close()