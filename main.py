# -*- coding: utf-8 -*-
"""
Created on Sat July 4 14:39:49 2021

@author: 木村　元紀
"""

from flask import Flask,request,abort
from linebot import (
    LineBotApi,WebhookHandler
    )
from linebot.exceptions import (
    InvalidSignatureError
    )
from linebot.models import(
    MessageEvent,TextMessage,TextSendMessage,
    FollowEvent)

import os
import datetime
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET_TOKEN = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET_TOKEN)

date_now = datetime.datetime.now()
#URL = "https://www.navitime.co.jp/bus/diagram/timelist?hour=3&departure=00031884&arrival=00031140&line=00009702&date={}-{}-{}".format(date_now.year,date_now.month,date_now.day)
URL = "https://www.navitime.co.jp/bus/diagram/timelist?hour=3&departure=00031884&arrival=00031140&line=00009702&date=2021-07-05"

@app.route("/")
def hello_line():
    return "Ok"

@app.route("/reply",methods=['POST'])
def reply_msg():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body:" + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK."

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

        
if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0',port=port)