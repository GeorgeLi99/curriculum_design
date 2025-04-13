# -*- coding: utf-8 -*-

import requests
import httpx
import bs4
import re
import pymysql as pms
import random
import time
from config import *

class Movie:
    def __init__(self, number, title, year, rating, comments, weight, similar, director, script, actors, types, 
                 country=None, language=None, release_date=None, runtime=None, aka=None, imdb=None):
        self.number = number
        self.title = title
        self.year = year
        self.rating = rating
        self.comments = comments
        self.weight = weight
        self.similar = similar
        self.director = director
        self.script = script
        self.actors = actors
        self.types = types
        # 新增字段
        self.country = country  # 制片国家
        self.language = language  # 语言
        self.release_date = release_date  # 上映日期
        self.runtime = runtime  # 片长
        self.aka = aka  # 又名
        self.imdb = imdb  # IMDb编号

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
        # 获取电影排名
        number = movie.find('span', attrs={"class": "top250-no"}).text.strip()
        print(f"电影排名: {number}")
        # 获取电影标题
        title = movie.find('span', attrs={"property": "v:itemreviewed"}).text.strip()
        print(f"电影标题: {title}")
        # 获取电影年份
        year = movie.find('span', attrs={"class": "year"}).text.strip()
        print(f"电影年份: {year}")
        # 获取电影评分
        rating = movie.find('strong', attrs={"class": "ll rating_num","property": "v:average"}).text.strip()
        print(f"电影评分: {rating}")
        # 获取电影评论数
        comments = movie.find('a', attrs={"href": "comments","class": "rating_people"}).find('span', attrs={"property": "v:votes"}).text.strip()
        print(f"电影评论数: {comments}")
        # 获取电影评分权重
        weight = movie.find('div', attrs={"class": "rating_on_weight"}).find_all('div',attrs={"class": "item"}).find('span',attrs={"class": "rating_per"}).text.strip()
        print(f"电影评分权重: {weight}")
        # 获取同类电影排名
        similar = movie.find_all('div', attrs={"class": "rating_betterthan"}).find('a').text.strip()
        print(f"同类电影排名: {similar}")
        # 获取电影信息区域
        info_div = movie.find('div', attrs={"id": "info"})
        if not info_div:
            print("未找到电影信息区域")
            info_div = soup.find('div', attrs={"id": "info"})  # 尝试从整个页面搜索
        
        # 创建电影剧组信息字典
        crew_info_dict = {}
        director = []
        script = []
        actors = []
        types = []
        
        # 初始化新增字段
        country = []
        language = []
        release_date = []
        runtime = None
        aka = []
        imdb = None

        if info_div:
            # 提取电影类型
            types = [t.text.strip() for t in info_div.find_all('span', attrs={"property": "v:genre"})]
            print(f"电影类型: {types}")
            
            # 专门提取上映日期
            release_dates = info_div.find_all('span', attrs={"property": "v:initialReleaseDate"})
            if release_dates:
                release_date = [date.text.strip() for date in release_dates]
                print(f"上映日期: {release_date}")
            
            # 专门提取片长
            runtime_span = info_div.find('span', attrs={"property": "v:runtime"})
            if runtime_span:
                runtime = runtime_span.text.strip()
                print(f"片长: {runtime}")
            
            # 遍历所有标签提取剧组信息及其他信息
            for label in info_div.find_all('span', class_='pl'):
                label_text = label.text.strip().rstrip(':')  # 移除冒号
                
                # 查找标签后的值
                values = []
                
                # 处理<span class="attrs">的情况
                next_attrs = label.find_next_sibling('span', class_='attrs')
                if next_attrs:
                    # 收集所有链接文本
                    values = [a.text.strip() for a in next_attrs.find_all('a')]
                else:
                    # 处理纯文本的情况
                    sibling = label.next_sibling
                    if sibling and isinstance(sibling, str) and sibling.strip():
                        values = [item.strip() for item in sibling.strip().split('/') if item.strip()]
                
                if values:
                    crew_info_dict[label_text] = values
                    print(f"{label_text}: {values}")
                    
                    # 提取各类信息
                    if '导演' in label_text:
                        director = values
                    elif '编剧' in label_text:
                        script = values
                    elif '主演' in label_text:
                        actors = values
                    elif '制片国家' in label_text or '制片地区' in label_text:
                        country = values
                    elif '语言' in label_text:
                        language = values
                    elif '又名' in label_text:
                        aka = values
                    elif 'IMDb' in label_text:
                        imdb = values[0] if values else None
                        
        print(f"电影剧组信息字典: {crew_info_dict}")
        print(f"电影导演: {director}")
        print(f"电影编剧: {script}")
        print(f"电影主演: {actors}")
        print(f"电影类型: {types}")
        print(f"制片国家: {country}")
        print(f"语言: {language}")
        print(f"上映日期: {release_date}")
        print(f"片长: {runtime}")
        print(f"又名: {aka}")
        print(f"IMDb编号: {imdb}")

        # 返回完整的实现可以返回电影对象
        return Movie(number, title, year, rating, comments, weight, similar, director, script, actors, types,
                     country, language, release_date, runtime, aka, imdb)

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
                movie_object = get_movie_info(movie)
                if movie_object:
                    save_to_mysql(movie_object)
            
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