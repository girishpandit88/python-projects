# iOSValidator.py
# @Author: Girish A Pandit
from flask import jsonify, request
from time import gmtime, strftime
from ConfigParser import SafeConfigParser

import json
import base64
import urllib2
import requests

class iOSValidator():
	moduleLoadTime=strftime("%Y-%m-%d %H:%M:%S", gmtime())
	iOSProdUrl=''
	iOSSandboxURL=''
	
	def __init__(self):
		parser = SafeConfigParser()
		parser.read('validationConfig')
		self.iOSProdUrl = parser.get('validationConfig', 'iOSProductionUrl')
		self.iOSSandboxUrl = parser.get('validationConfig', 'iOSSandboxUrl')

	def validateIOS7Receipt(self, receipt, transcationId):
		if "1-" in transcationId:
			transcationId=transcationId[2:]
		jsonData = json.dumps({'receipt-data': receipt})
		response = requests.post(self.iOSProdUrl, data=jsonData).json()
		if response['status']==21007:
			return self.validateSandbox7Receipt(jsonData,transcationId)
		responseJSON = jsonify(status=response['status'])
		return responseJSON

	def validateSandbox7Receipt(self, data,transactionId):
		response = requests.post(self.iOSSandboxUrl, data=data).json()
		inAppReceipts = response['receipt']['in_app']
		print "Len:"+str(len(inAppReceipts))
		if response['status']==0:
			for inAppReceipt in inAppReceipts:
				if transactionId == inAppReceipt['original_transaction_id']:
					responseJSON = self.prepareResponse(response)
					break
				else:
					responseJSON = self.prepareResponse(None)
		return responseJSON

	def prepareResponse(self, res):
		if res is None:
			responseJSON = jsonify(status='-10001',message='Could not verify receipt')
			responseJSON.status_code = 404
			return responseJSON
		responseJSON = jsonify(status=res['status'], receiptType=res['environment'])
		responseJSON.status_code = 200
		return responseJSON


