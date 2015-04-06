#inAppValidator
# @Author: Girish A Pandit

from flask import Flask, jsonify, request
from time import gmtime, strftime
import json
from ConfigParser import SafeConfigParser
import base64
import urllib2
import requests

app = Flask(__name__)
moduleLoadTime=strftime("%Y-%m-%d %H:%M:%S", gmtime())
iOSProdUrl=''
iOSSandboxURL=''

def loadConfig():
	parser = SafeConfigParser()
	parser.read('validationConfig')
	app.config['iOSProdUrl'] = parser.get('validationConfig', 'iOSProductionUrl')
	app.config['iOSSandboxUrl'] = parser.get('validationConfig', 'iOSSandboxUrl')

@app.route("/mtx/recordTransaction", methods=['POST'])
def recordTransaction():
	data = request.data
	dataDict = json.loads(data)
	if dataDict['platform'] in "iOS":
		return validateIOS7Receipt(dataDict['receipt'],dataDict['transactionId'])
	else:
		response = jsonify(message="Platform currently not supported")
		response.status_code=200
		return response
	response= jsonify(success=True)
	response.status_code=200
	return response

def validateIOS7Receipt(receipt, transcationId):
	loadConfig()
	if "1-" in transcationId:
		transcationId=transcationId[2:]
	jsonData = json.dumps({'receipt-data': receipt})
	response = requests.post(app.config['iOSProdUrl'], data=jsonData).json()
	if response['status']==21007:
		return validateSandbox7Receipt(jsonData,transcationId)
	responseJSON = jsonify(status=response['status'])
	return responseJSON

def validateSandbox7Receipt(data,transactionId):
	response = requests.post(app.config['iOSSandboxUrl'], data=data).json()
	inAppReceipts = response['receipt']['in_app']
	print "Len:"+str(len(inAppReceipts))
	if response['status']==0:
		for inAppReceipt in inAppReceipts:
			if transactionId == inAppReceipt['original_transaction_id']:
				responseJSON = prepareResponse(response)
				break
			else:
				responseJSON = prepareResponse(None)
	return responseJSON

def prepareResponse(res):
	if res is None:
		responseJSON = jsonify(status='-10001',message='Could not verify receipt')
		responseJSON.status_code = 404
		return responseJSON
	responseJSON = jsonify(status=res['status'], receiptType=res['environment'])
	responseJSON.status_code = 200
	return responseJSON

@app.route("/sysstat")
def sysstat():
	response= jsonify(loadTime=moduleLoadTime)
	response.status_code=200
	return response		

if __name__ == "__main__":
    app.run()