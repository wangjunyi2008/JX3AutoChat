import datetime

VERSION = 0.3
STARTTIME = datetime.datetime.now()
debugname = "debug.txt"

var = {}
var["TIEBA_UPDATE_TO"] = ""
var['TIEBA_SHIDA'] = []
var['TIEBA_SHIDA_UPDATE'] = ""
var['TIEBA_UPDATETIME'] = "18-00"

def set_value(svar,value):
	var[svar] = value

def get_value(svar):
	return var[svar]