# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode
import xml.etree.ElementTree as ET
import urllib,urllib2,time,hashlib
import json

TOKEN = "*****"
API_KEY = 'b***************11c19342f5f0274'
USER_ID=49***


@csrf_exempt
def handleRequest(request):
	if request.method == 'GET':
		response = HttpResponse(checkSignature(request),content_type="text/plain")
		return response
	elif request.method == 'POST':
		response = HttpResponse(responseMsg(request),content_type="application/xml")
		return response
	else:
		return None

def checkSignature(request):
	global TOKEN
	signature = request.GET.get("signature", None)
	timestamp = request.GET.get("timestamp", None)
	nonce = request.GET.get("nonce", None)
	echoStr = request.GET.get("echostr",None)
	token = TOKEN
	tmpList = [token,timestamp,nonce]
	tmpList.sort()
	tmpstr = "%s%s%s" % tuple(tmpList)
	tmpstr = hashlib.sha1(tmpstr).hexdigest()
	if tmpstr == signature:
		return echoStr
	else:
		return None

def responseMsg(request):
	rawStr = smart_str(request.raw_post_data)
	#rawStr = smart_str(request.POST['XML'])
	msg = paraseMsgXml(ET.fromstring(rawStr))
	queryStr = msg.get('Content','You have input nothing~')
	raw_tulingURL = "http://www.tuling123.com/openapi/api?key=%s&%s&info=" % (API_KEY,USER_ID)	
	tulingURL = "%s%s" % (raw_tulingURL,urllib2.quote(queryStr))
	req=urllib2.Request(tulingURL)
	raw_json=urllib2.urlopen(req).read()
	hjson=json.loads(raw_json)
	length=len(hjson.keys())
	content=hjson['text'].encode('utf-8')
	if length==3:
		replyContent= "%s%s"%(content,hjson['url'].encode('utf-8'))
	elif length==2:
		replyContent= content
	else:
		return "please input again."
	replyContent = content
	return getReplyXml(msg,replyContent)

def paraseMsgXml(rootElem):
	msg = {}
	if rootElem.tag == 'xml':
		for child in rootElem:
			msg[child.tag] = smart_str(child.text)
	return msg


def getReplyXml(msg,replyContent):
	for i in range(1,1000):
		extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
		extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
		return extTpl

