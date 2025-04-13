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
    print(proxies)
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

# 使用随机 IP 请求页面
def request_with_random_ip(url):
    # 每次请求前随机选择新的IP代理
    proxy = get_ip()
    print(f"使用代理: {proxy}")
    
    try:
        # 发起请求
        res = requests.get(url, headers=headers, proxies=proxy, timeout=15, verify=False)
        if res.status_code == 200:
            print("请求成功!")
            return res
        else:
            print(f"请求失败: 状态码 {res.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

# 预先定义电影信息提取函数
def get_movie_info(movie):
    # TODO: Implement movie info extraction
    try:
        title = movie.find('span', class_='title').text.strip()
        print(f"电影标题: {title}")
        # 返回完整的实现可以返回电影对象
        return title
    except Exception as e:
        print(f"解析电影信息失败: {e}")
        return None

def crawl_page(url,page=0):
    # 使用随机代理发送请求
    print(f"开始爬取豆瓣电影Top250第{page+1}页...")
    res = request_with_random_ip(url)
    
    # 如果请求成功，解析页面内容
    if res:
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        try:
            movie_list = soup.find('ol', class_='grid_view').find_all('li')
            print(f"找到 {len(movie_list)} 部电影")
        
            # 对每部电影进行处理
            for movie in movie_list:
                get_movie_info(movie)
            
            # 每次请求后随机延时
            delay = random.randint(START_TIME, END_TIME)
            print(f"延时 {delay} 秒...")
            time.sleep(delay)
        except Exception as e:
            print(f"解析页面失败: {e}")
    else:
        print("请求失败，无法获取页面内容")

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

    sql = "INSERT INTO movies (title, rating, year, quote) VALUES (%s, %s, %s, %s)"

    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()

if __name__=="__main__":
    # 代码中的主逻辑已经直接运行
    # 如果需要将电影信息存入数据库，可以将下面的代码取消注释
    # save_to_mysql()
