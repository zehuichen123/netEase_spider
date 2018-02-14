#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author : lovesnowbest
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import pymysql

header={
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
datas = {
    'uid': '107948356',
    'type': '0',
    'params': 'omVn+M+0MLjIZemA9918G3f5KdkNonc9V858JCrRutQEUSoFW9d5+RjfEooWwEkm4L0FduF4tveH9frjgEPfBVcIKeMI+CMJQr9F9Rj/J370mfSjFzTH3M8R8EUUO1JmECbzdtXEaDQ9LJILWDBR8FE9zINdgO2F4FF8YYwclm35Og06qR7SXleDG0ZInf3MUWotx/i/7JodxnfsS9nzrw==',
    'encSecKey': '5eea474d42a3dbaa409d73a1fa71594616c770cc0e38f701f233c410001d604ef868df63441359098d9055ba8abf16e8a1523c3ac56023c1c4a43f9282a8fa5902b60fc3224605304586571a64fea107b1392a75595cfdbbae461427b449a14b91a5d932aad5c8269eb7aecead13d2aa6980630e48929b47a3a40962694443bb'
}

sender='672604803@qq.com'
password='***************'   #就是上面的那张照片里的密码
user='lovesnowbest@gmail.com' #这里可以指定发给多个人
netEaseDb=pymysql.connect('localhost','root',
        '*************','netEase',charset='utf8')

cursor=netEaseDb.cursor()

class urlManager(object):
    def __init__(self):
        self.new_ids=set()

    def has_new_id(self):
        return self.new_id_size()!=0

    def get_new_id(self):
        new_id=self.new_ids.pop()
        return new_id

    def find_old_id(self,new_id):
        sql=""" select * from userinfo where uid='%s'"""%new_id
        try:
            cursor.execute(sql)
            results=cursor.fetchall()
            if len(results)==0:
                return True
            else:
                return False
        except Exception as e:
            print(e)

    def add_new_id(self,new_id):
        if new_id is None or self.new_id_size()+self.old_id_size()>20 or self.new_id_size()>10:
            return
        if new_id not in self.new_ids and self.find_old_id(new_id): 
            self.new_ids.add(new_id)

    def add_new_ids(self,new_ids):
        if new_ids is None or len(new_ids)==0:
            return
        for new_id in new_ids:
            self.add_new_id(new_id)

    def new_id_size(self):
        return len(self.new_ids)

    def old_id_size(self):
        sql="""select count(*) from userinfo"""
        try:
            cursor.execute(sql)
            results=cursor.fetchall()
        except Exception as e:
            print(e)
        return results[0][0]

class htmlManager(object):
    def getUserInfo(self,new_id):
        url="http://music.163.com/user/home?id=" + str(new_id)
        
        user={}
        req=requests.get(url,headers=header)
        req_bs=BeautifulSoup(req.text,'html.parser')

        infoArea=req_bs.findAll("h2",{"id":"j-name-wrap"})
        infoArea_bs=BeautifulSoup(str(infoArea),'html.parser')
        user["uid"]=str(new_id)
        user["name"]=infoArea_bs.find("span",{"class":"tit f-ff2 s-fc0 f-thide"}).text
        user["level"]=infoArea_bs.find("span",{"class":"lev u-lev u-icn2 u-icn2-lev"}).text
        sexInfo=infoArea_bs.findAll("i")[-1]["class"][-1][-1]
        if sexInfo=='1':
            user['sex']='male'
        else:
            user['sex']='female'
        song=req_bs.find("div",{"id":"rHeader"}).find("h4").text
        songNum=int(song[4:-1])
        user["songNum"]=songNum
        return user

    def getUserFollower(self,new_id):
        url = 'http://music.163.com/weapi/user/getfollows/%s?csrf_token=' % str(new_id)
        response=requests.post(url,headers=header,data=datas).content
        json_text=json.loads(response.decode('utf-8'))
        followers=json_text['follow']
        new_ids=[]
        for new_id in followers:
            new_ids.append(new_id['userId'])
        return new_ids

class dataOutput(object):
    def __init__(self):
        pass

    def output_data(self,info):  
        if info is None:
            return
        sql=""" insert into userinfo(sex,songNum,level,name,uid)
                VALUES('%s','%s','%s','%s','%s')"""%(info['sex'],info['songNum'],info['level'],info['name'],info['uid'])
        try:
            cursor.execute(sql)
            netEaseDb.commit()
        except Exception as e:
            print(e)
            netEaseDb.rollback()
            netEaseDb.close()

class netEaseSpider(object):
    def __init__(self):
        self.manager=urlManager()
        self.parser=htmlManager()
        self.output=dataOutput()

    def crawl(self,root_id):
        self.manager.add_new_id(root_id)
        while (self.manager.has_new_id() and self.manager.old_id_size()<20):
            try:
                new_id=self.manager.get_new_id()
                user=self.parser.getUserInfo(new_id)
                followers_id=self.parser.getUserFollower(new_id)
                self.manager.add_new_ids(followers_id)
                self.output.output_data(user)
                print('has get %s ids'%self.manager.old_id_size())
            except Exception as e:
                print(e)
 

def mail(cond):
    #邮件的内容
    if cond==0:
        msg=MIMEText('您的爬虫不幸终止😭','plain','utf-8')
    else:
        msg=MIMEText('您的爬虫已经完成✅','plain','utf-8')
    #括号内对应发件人的昵称和发件人的账号
    msg['From']=formataddr(["loveSnowBest",sender])
    #括号内对应收件人的昵称和收件人的账号
    msg['To']=formataddr(["xxx",user])
    #邮件的主题
    msg['Subject']="netEase spider"
    #发件人邮箱中的SMTP服务器 
    server=smtplib.SMTP_SSL("smtp.qq.com",465)
    #登陆
    server.login(sender,password)
    #括号内对应发件人，收件人，邮件信息
    server.sendmail(sender,[user,],msg.as_string())
    server.quit()


myspider=netEaseSpider()
try:
    myspider.crawl("136702185")
    mail(1)
except Exception as e:
    print(e)
    mail(0)







