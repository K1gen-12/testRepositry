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

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET_TOKEN = os.environ['YOUR_CHANNEL_SECRET']

@app.route("/",methods=['POST'])
def hello_line():
    print("Enter Line...")
    return "Ok"

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0',port=port)