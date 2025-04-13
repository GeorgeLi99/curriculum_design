#! -*- encoding:utf-8 -*-

import requests
import httpx
import beautifulsoup4 as bs4
import parsel
import re
import pymysql as pms
import random
import time
from config import *

ip_list=[]
with open('ip.txt','r') as file:
    ip_list=file.readlines()

def get_ip():
    proxy=ip_list[random.randint(0,len(ip_list)-1)]
    proxy=proxy.replace('\r\n','')
    proxies={
        'http':'http://'+str(proxy),
        # 'https':'https://'+str(proxy)
    }   
    return proxies  # request 的ip代理约定格式

headers={
    'Host':'movie.douban.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'cookie':'bid=uVCOdCZRTrM; douban-fav-remind=1; __utmz=30149280.1603808051.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __gads=ID=7ca757265e2366c5-22ded2176ac40059:T=1603808052:RT=1603808052:S=ALNI_MYZsGZJ8XXb1oU4zxzpMzGdK61LFA; _pk_ses.100001.4cf6=*; __utma=30149280.1867171825.1603588354.1603808051.1612839506.3; __utmc=30149280; __utmb=223695111.0.10.1612839506; __utma=223695111.788421403.1612839506.1612839506.1612839506.1; __utmz=223695111.1612839506.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=223695111; ap_v=0,6.0; __utmt=1; dbcl2="165593539:LvLaPIrgug0"; ck=ZbYm; push_noty_num=0; push_doumail_num=0; __utmv=30149280.16559; __utmb=30149280.6.10.1612839506; _pk_id.100001.4cf6=e2e8bde436a03ad7.1612839506.1.1612842801.1612839506.',
    'accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
}
url='https://movie.douban.com/top250'

res=requests.get(url,headers=headers,proxies=get_ip(),verify=False)

soup=bs4.BeautifulSoup(res.text,'html.parser')

def save_to_mysql():
    # 建立数据库连接
    conn=pms.connect(
        host='localhost',
        user='root',
        password=PASSWORD,
        database=DATABASE,
        charset='utf8mb4'
    )

    cursor = conn.cursor()

    # 创建数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        year INT,
        rating DECIMAL(3,1),
        quote VARCHAR(255)
    )
    ''')

    sql = "INSERT INTO movies (title,rating,year,director,actors,)"

    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()


time.sleep(random.randint(3,5))