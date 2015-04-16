#inAppValidator.py
# @Author: Girish A Pandit

from flask import Flask, jsonify, request
from time import gmtime, strftime
from boto.dynamodb2.layer1 import DynamoDBConnection
from ConfigParser import SafeConfigParser
from validators import iOSValidator
from storetransactions import storeTransactions

import json
import base64
import urllib2
import requests

app = Flask(__name__)
iOSValidator = iOSValidator()
transactionMgr = storeTransactions()
@app.route("/mtx/transactions/verify", methods=['POST'])
def recordTransaction():
	data = request.data
	dataDict = json.loads(data)
	if dataDict['platform'] in "iOS":
		response =  iOSValidator.validateIOS7Receipt(dataDict['receipt'],dataDict['transactionId'])
		with open('tmp.csv','rw') as f:
			t= (dataDict['receipt'],dataDict['transactionId'],dataDict['price'],strftime("%Y-%m-%d %H:%M:%S", gmtime()))
			f.write(" ".join(t))
			f.seek(0)
			print 'Key:'+str(transactionMgr.storeToS3(f))
			f.close()
		return response
	else:
		response = jsonify(message="Platform currently not supported")
		response.status_code=200
		return response
	response= jsonify(success=True)
	response.status_code=200
	return response

@app.route("/sysstat")
def sysstat():
	response= jsonify(loadTime=moduleLoadTime)
	response.status_code=200
	return response		

if __name__ == "__main__":
    app.run(debug=True)