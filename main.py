# -*- coding: utf-8 -*-
"""
Created on Sat July 4 14:39:49 2021

@author: 木村　元紀
"""
from bs4 import BeautifulSoup
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
import requests
import datetime

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET_TOKEN = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET_TOKEN)
date_now = datetime.datetime.now()

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
    
@handler.add(MessageEvent,message=TextMessage)
def tell_bustime_iki(event):
    tz = datetime.timezone(datetime.timedelta(hours=9),name='JAPAN')
    date_now = datetime.datetime.now(tz)
    URL ="https://www.navitime.co.jp/bus/diagram/timelist?hour=3&departure=00031884&arrival=00031140&line=00009702&date={}-{}-{}".format(date_now.year,date_now.month,date_now.day)
    cnt_h=0
    cnt_m=0
    if event.type == "message":
        if (event.message.text=="バス")or(event.message.text=="バスの時間")or(event.message.text=="バスの時刻表")or(event.message.text=="ばす"):
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="現在片道のみ利用可能。「行き(いき）」と入力してください"))
            
        if (event.message.text=="いき")or(event.message.text=="行き"):
            
            res = requests.get(URL)
            soup = BeautifulSoup(res.content,"html.parser")
            soup = soup.find(class_='left wide-page-mode')
            soup = soup.find(class_="time-list-frame")
            Hours = soup.find_all("dt")
            
            try:
                for i in Hours:
                    i = i.text
                    i = i.replace("時","")
                    i = int(i)
                
                    if (i<date_now.hour):
                        cnt_h+=1
                        print(i)
                    else:
                        break
                
                time = Hours[cnt_h].text
                time = time.replace("時","")
            
                Mins = soup.find_all("dd")
                Mins = Mins[cnt_h].find("ol")
                Mins = Mins.find_all(class_="time-detail")
            
                for j in Mins:
                    Min = j.find(class_="time dep")
                    Min = Min.text
                    Min = Min.replace(time+":","")
                    Min = int(Min)
                
                    if(Min<date_now.minute):
                        cnt_m+=1
                    else:
                        cnt_m=0
                        break
                
                TIME_d = Mins[cnt_m].find(class_="time dep")
                TIME_d = TIME_d.text
                TIME_a = Mins[cnt_m].find(class_="time arr")
                TIME_a = TIME_a.text
                TEXT_BT = TIME_d+"=>"+TIME_a
    
                line_bot_api.reply_message(event.reply_token, TextSendMessage(TEXT_BT))
                
            except IndexError:
                print("Error:Out of time")
                line_bot_api.reply_message(event.reply_token, TextSendMessage("対象のバスが見つかりません"))

@handler.add(MessageEvent,message=TextMessage)
def tell_bustime_kaeri(event):
    cnt_h=0
    cnt_m=0
    tz = datetime.timezone(datetime.timedelta(hours=9),name='JAPAN')
    date_now = datetime.datetime.now(tz)
    URL ="https://www.navitime.co.jp/bus/diagram/timelist?hour=3&departure=00031140&arrival=00031884&line=00009702&date={}-{}-{}".format(date_now.year,date_now.month,date_now.day)
    
    response = requests.get(URL)
    soup =BeautifulSoup(response.content,"html.parser")
    soup = soup.find(class_="left wide-page-mode")
    soup = soup.find(class_="time-list-frame")
    hours = soup.find_all("dt")
    
    try:
        for i in hours:
            i = i.text
            i = i.replace("時","")
            i = int(i)
            
            if (i<date_now.hour):
                cnt_h+=1
            else:
                cnt_h=0
                break
        
        time = hours[cnt_h].text
        time = time.replace("時","")
            
        Mins = soup.find_all("dd")
        Mins = Mins[cnt_h].find("ol")
        Mins = Mins.find_all(class_="time-detail")
        
        for j in Mins:
            Min = j.find(class_="time dep")
            Min = Min.text
            Min = Min.replace(time+":","")
            Min = int(Min)
            
            if(Min<date_now.minute):
                cnt_m+=1
            else:
                cnt_m=0
                break
            
        TIME_d = Mins[cnt_m].find(class_="time dep")
        TIME_d = TIME_d.text
        TIME_a = Mins[cnt_m].find(class_="time arr")
        TIME_a = TIME_a.text
        text = TIME_d+"=>"+TIME_a
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text))
            
    except IndexError:
        print("out of time") 
        line_bot_api.reply_message(event.reply_token, TextSendMessage("対象のバスが見つかりません"))
        
if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0',port=port)