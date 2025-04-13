# -*- coding: utf-8 -*-

import requests
import httpx
import bs4
import re
import pymysql
import random
import time
from config import *

class Movie:
    def __init__(self, number, title, year, rating, comments_num, weight, similar, director, script, actors, types, 
                 country=None, language=None, release_date=None, runtime=None, aka=None, imdb=None, comments=None):
        # 电影排名
        self.number = number
        # 电影标题
        self.title = title
        # 电影年份
        self.year = year
        # 电影评分
        self.rating = rating
        # 电影评论数
        self.comments_num = comments_num
        # 电影评论对象列表
        self.comments = comments    
        # 电影评分权重
        self.weight = weight
        # 同类电影排名
        self.similar = similar
        # 电影导演
        self.director = director
        # 电影编剧
        self.script = script
        # 电影演员
        self.actors = actors
        # 电影类型
        self.types = types
        # 制片国家
        self.country = country
        # 语言
        self.language = language
        # 上映日期
        self.release_date = release_date
        # 片长
        self.runtime = runtime
        # 又名
        self.aka = aka
        # IMDb编号
        self.imdb = imdb
class Comment:
    def __init__(self,movie_id,comment,star,comment_time,comment_person,comment_vote):
        # 电影ID
        self.movie_id = movie_id
        # 评论内容
        self.comment = comment
        # 评分
        self.star = star
        # 评论时间
        self.comment_time = comment_time
        # 评论人
        self.comment_person = comment_person
        # 评论票数
        self.comment_vote = comment_vote

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

def get_comment_info(comment_soup, movie_id):
    # 从评论页提取评论完整信息
    try:
        # 提取评论投票数
        comment_vote_span = comment_soup.find('span', attrs={'class':'comment-vote'})
        if comment_vote_span:
            vote_count_span = comment_vote_span.find('span', attrs={'class':'votes vote-count'})
            comment_vote = vote_count_span.text.strip() if vote_count_span else "0"
        else:
            comment_vote = "0"
        
        # 提取评论信息区域
        comment_info = comment_soup.find('span', attrs={'class':'comment-info'})
        
        # 提取评论人
        comment_person_tag = comment_info.find('a', attrs={'href':True}) if comment_info else None
        comment_person = comment_person_tag.text.strip() if comment_person_tag else "未知用户"
        
        # 提取评分 - 注意星级的类名通常包含星级的信息，如“allstar50 rating”
        star_span = comment_info.find('span', attrs={'class': lambda c: c and 'rating' in c}) if comment_info else None
        if star_span:
            # 从类名中提取星级，例如“allstar50”表示5星
            star_class = star_span.get('class', [])
            star_rating = None
            for cls in star_class:
                if cls.startswith('allstar'):
                    try:
                        # 尝试将“allstar50”转换为“5星”
                        rating_num = int(cls.replace('allstar', '')) / 10
                        star_rating = f"{rating_num}星"
                        break
                    except:
                        pass
            comment_star = star_rating or star_span.text.strip() or "无评分"
        else:
            comment_star = "无评分"
        
        # 提取评论时间
        time_span = comment_info.find('span', attrs={'class':'comment-time'}) if comment_info else None
        comment_time = time_span.get('title', time_span.text.strip()) if time_span else "未知时间"
        
        # 提取评论内容
        content_p = comment_soup.find('p', attrs={'class':'comment-content'})
        if content_p:
            short_span = content_p.find('span', attrs={'class':'short'})
            comment = short_span.text.strip() if short_span else content_p.text.strip()
        else:
            comment = "无评论内容"
        
        return Comment(movie_id, comment, comment_star, comment_time, comment_person, comment_vote)
    except Exception as e:
        print(f"解析评论信息失败: {e}")
        # 返回一个带有默认值的评论对象
        return Comment(movie_id, "解析失败", "无评分", "未知时间", "未知用户", "0")

# 预先定义电影信息提取函数
def get_movie_info(movie_soup, number, movie_url):
    # 从详情页提取电影完整信息
    try:
        # 排名已经从列表页提取
        # 不在这里打印，只在函数最后汇总打印
        
        # 获取电影标题
        title = movie_soup.find('span', attrs={"property": "v:itemreviewed"}).text.strip()
        
        # 获取电影年份
        year = movie_soup.find('span', attrs={"class": "year"}).text.strip()
        # 获取电影评分
        rating_elem = movie_soup.find('strong', attrs={"class": "ll rating_num", "property": "v:average"})
        rating = rating_elem.text.strip() if rating_elem else "0.0"
        
        # 获取电影评论数
        votes_elem = movie_soup.find('span', attrs={"property": "v:votes"})
        comments_num = votes_elem.text.strip() if votes_elem else "0"
        
        # 获取电影评分权重 - 提取所有星级的权重
        weight_dict = {}
        weight_wrapper = movie_soup.find('div', attrs={"class": "ratings-on-weight"})
        if weight_wrapper:
            # 查找所有星级评分权重项
            weight_items = weight_wrapper.find_all('div', attrs={"class": "item"})
            
            for item in weight_items:
                # 星级名称（如"5星"）
                star_elem = item.find('span', attrs={"class": "rating_per"})
                # 该星级的占比
                percentage = star_elem.text.strip() if star_elem else "0%"
                
                # 星级数字（从前面得到）
                star_count_elem = item.find('span', {'class': lambda x: x and x.startswith('star')})
                if star_count_elem:
                    star_class = star_count_elem.get('class', [])
                    star_level = ''
                    for cl in star_class:
                        if cl.startswith('star'):
                            star_level = cl.replace('star', '') + '星'  # 增加"星"字
                            break
                    
                    if star_level:
                        weight_dict[star_level] = percentage
            
            # 将字典转换为字符串形式
            if weight_dict:
                weight = " | ".join([f"{k}: {v}" for k, v in weight_dict.items()])
            else:
                weight = "0%"  # 默认值
        
        # 获取同类电影排名
        similar_list = []
        betterthan = movie_soup.find('div', attrs={"class": "rating_betterthan"})
        if betterthan:
            # 提取所有同类电影排名信息
            similar_a_tags = betterthan.find_all('a')
            if similar_a_tags:
                similar_list = [a.text.strip() for a in similar_a_tags]
                similar = ", ".join(similar_list)  # 将多个排名用逗号连接
            else:
                similar = ""
        
        # 获取电影信息区域
        info_div = movie_soup.find('div', attrs={"id": "info"})
        if not info_div:
            print("未找到电影信息区域")
            return None
        
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
            
            # 专门提取上映日期
            release_dates = info_div.find_all('span', attrs={"property": "v:initialReleaseDate"})
            if release_dates:
                release_date = [date.text.strip() for date in release_dates]
            
            # 专门提取片长
            runtime_span = info_div.find('span', attrs={"property": "v:runtime"})
            if runtime_span:
                runtime = runtime_span.text.strip()
            
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
                    # 提取各类信息并存储，但不立即打印
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
                        
        # 完整的电影信息汇总打印
        print(f"电影排名: {number}")
        print(f"电影标题: {title}")
        print(f"电影年份: {year}")
        print(f"电影评分: {rating}")
        print(f"电影评论数: {comments_num}")
        print(f"电影权重: {weight}")
        if similar:
            print(f"同类电影排名: 超过 {similar}")
        else:
            print("同类电影排名: 无")
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
        print("-" * 105)  # 添加分隔线

        # 传入当前电影ID和电影页面对象
        comment_objects = crawl_comment(number, movie_soup)
        if comment_objects:
            print(f"共获取了 {len(comment_objects)} 条评论")
        else:
            print("未获取到评论")

        # 返回完整的实现可以返回电影对象
        return Movie(number, title, year, rating, comments_num, weight, similar, director, script, actors, types,
                     country, language, release_date, runtime, aka, imdb, comment_objects)

    except Exception as e:
        print(f"解析电影信息失败: {e}")
        return None

def crawl_comment(movie_id, movie_soup):
    count=0
    comment_url=movie_soup.find('div',attrs={'id':'comments-section'}).find('div',attrs={'id':'hot-comments'}).find('a',attrs={'href':True})['href']
    detail_request=request_with_random_ip(comment_url)
    if detail_request:
        comment_soup=bs4.BeautifulSoup(detail_request.text,'html.parser')
        comments=comment_soup.find_all('div',attrs={'class':'comment-item','data-cid':True})
        
        # 获取所有评论，但只打印第一个
        comment_objects = []
        for comment in comments:
            comment_object = get_comment_info(comment, movie_id)
            comment_objects.append(comment_object)
            count+=1
        
        while(count<60):
            next_url=comment_soup.find('div',attrs={'id':'paginator','class':'center'}).find('a',attrs={'href':True,'data-page':'next','class':'next'})['href']
            detail_request=request_with_random_ip(next_url)
            if detail_request:
                comment_soup=bs4.BeautifulSoup(detail_request.text,'html.parser')
                comments=comment_soup.find_all('div',attrs={'class':'comment-item','data-cid':True})
                for comment in comments:
                    comment_object = get_comment_info(comment, movie_id)
                    comment_objects.append(comment_object)
                    count+=1
                    
        # 打印第一个评论
        if comment_objects and len(comment_objects) > 0:
            print(f"共获取了 {len(comment_objects)} 条评论，显示第一条：")
            print(f"评论人: {comment_objects[0].comment_person}")
            print(f"评论内容: {comment_objects[0].comment}")
            print(f"评论星级: {comment_objects[0].star}")
            print(f"评论时间: {comment_objects[0].comment_time}")
            print(f"评论票数: {comment_objects[0].comment_vote}")
            print("-" * 105)  # 添加分隔线
        return comment_objects
    else:
        print("未获取到评论")
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
                # 提取电影排名
                number_elem = movie.find('em')
                number = number_elem.text.strip() if number_elem else "未知"
                print(f"电影排名: {number}")
                
                # 提取电影详情页URL
                movie_url = movie.find('a', attrs={'href': True})['href']
                print(f"发现电影URL: {movie_url}")
                
                # 访问电影详情页
                print(f"正在访问电影详情页...")
                detail_res = request_with_random_ip(movie_url)
                
                if detail_res:
                    # 解析电影详情页
                    movie_soup = bs4.BeautifulSoup(detail_res.text, 'html.parser')
                    # 从详情页提取电影信息
                    movie_object = get_movie_info(movie_soup, number, movie_url)
                    if movie_object:
                        try:
                            save_to_mysql(movie_object)
                        except Exception as e:
                            print(f"警告: 保存到数据库失败，继续爬取下一部电影: {e}")
                else:
                    print(f"访问电影详情页失败")
                
                # 在电影之间添加小延时避免被反爬
                item_delay = random.randint(START_TIME, END_TIME)
                print(f"电影间隔延时 {item_delay} 秒...")
                time.sleep(item_delay)
            
            # 每次请求后随机延时
            delay = random.randint(START_TIME, END_TIME)
            print(f"延时 {delay} 秒...")
            time.sleep(delay)

        except Exception as e:
            print(f"解析页面失败: {e}")
    else:
        print("请求失败，无法获取页面内容")

def save_to_mysql(movie):
    # 建立数据库连接
    try:
        conn=pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            charset='utf8mb4'
        )

        cursor = conn.cursor()
        
        # 返回当前连接和游标供保存评论使用
        return save_movie_to_mysql(movie, conn, cursor)
    except Exception as e:
        print(f"建立数据库连接失败: {e}")
        return None

def save_movie_to_mysql(movie, conn=None, cursor=None):
    # 如果没有提供连接和游标，创建新的连接
    close_conn = False  # 是否需要关闭连接
    if conn is None or cursor is None:
        try:
            conn=pymysql.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            close_conn = True  # 在函数内创建的连接需要在函数结束时关闭
        except Exception as e:
            print(f"建立数据库连接失败: {e}")
            return None

    try:

        # 创建数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            year VARCHAR(10),
            rating DECIMAL(3,1),
            comments_num INT,
            comments TEXT,
            director TEXT,
            script TEXT,
            actors TEXT,
            types TEXT,
            country TEXT,
            language TEXT,
            release_date TEXT,
            runtime VARCHAR(50),
            aka TEXT,
            imdb VARCHAR(20)
        )
        ''')
        
        # 创建评论表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id INT NOT NULL,           -- 外键关联到电影表
            comment_text TEXT NOT NULL,      -- 评论内容
            comment_star VARCHAR(20),       -- 评分
            comment_time VARCHAR(50),        -- 评论时间
            comment_person VARCHAR(100),     -- 评论人
            comment_vote INT,                -- 评论有用数
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
        ''')

        # 准备数据 - 将列表转换为字符串
        directors_str = ','.join(movie.director) if movie.director else ''
        script_str = ','.join(movie.script) if movie.script else ''
        actors_str = ','.join(movie.actors) if movie.actors else ''
        types_str = ','.join(movie.types) if movie.types else ''
        country_str = ','.join(movie.country) if movie.country else ''
        language_str = ','.join(movie.language) if movie.language else ''
        release_date_str = ','.join(movie.release_date) if movie.release_date else ''
        aka_str = ','.join(movie.aka) if movie.aka else ''

        # 插入数据
        sql = """INSERT INTO movies (title, year, rating, comments_num, comments, director, script, actors, 
                      types, country, language, release_date, runtime, aka, imdb) 
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (
            movie.title, 
            movie.year, 
            movie.rating, 
            movie.comments_num,
            movie.comments,  # 这里现在是评论内容字段，不是对象列表
            directors_str,
            script_str,
            actors_str,
            types_str,
            country_str,
            language_str,
            release_date_str,
            movie.runtime,
            aka_str,
            movie.imdb
        ))

        # 提交事务
        conn.commit()
        
        # 获取插入的电影ID
        movie_id = cursor.lastrowid
        print(f"电影 {movie.title} 保存到数据库成功，ID: {movie_id}")
        
        # 如果电影有评论对象列表，则保存评论
        if hasattr(movie, 'comments') and isinstance(movie.comments, list) and len(movie.comments) > 0:
            save_comments_to_mysql(movie_id, movie.comments, conn, cursor)
        
        # 如果是在函数内创建的连接，需要关闭
        if close_conn:
            cursor.close()
            conn.close()
            
        return movie_id
        
    except Exception as e:
        print(f"保存到数据库失败: {e}")
        return None

def save_comments_to_mysql(movie_id, comment_objects, conn=None, cursor=None):
    """将评论对象列表保存到数据库评论表中
    
    Args:
        movie_id (int): 电影ID，外键关联到电影表
        comment_objects (list): Comment对象列表
        conn: 可选数据库连接
        cursor: 可选数据库游标
        
    Returns:
        int: 成功插入的评论数量
    """
    # 如果没有提供连接和游标，创建新的连接
    close_conn = False  # 是否需要关闭连接
    if conn is None or cursor is None:
        try:
            conn=pymysql.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            close_conn = True  # 在函数内创建的连接需要在函数结束时关闭
        except Exception as e:
            print(f"建立数据库连接失败: {e}")
            return 0
    
    try:
        # 准备插入SQL
        sql = """INSERT INTO comments (movie_id, comment_text, comment_star, comment_time, comment_person, comment_vote)
              VALUES (%s, %s, %s, %s, %s, %s)"""
        
        # 记录成功插入的记录数
        success_count = 0
        
        # 逐个处理评论对象
        for comment in comment_objects:
            try:
                # 将评论票数转换为整数
                try:
                    vote = int(comment.comment_vote) if comment.comment_vote else 0
                except:
                    vote = 0
                    
                cursor.execute(sql, (
                    movie_id,
                    comment.comment,  # 评论内容
                    comment.star,     # 评分
                    comment.comment_time,  # 评论时间
                    comment.comment_person,  # 评论人
                    vote  # 评论票数
                ))
                success_count += 1
            except Exception as e:
                print(f"保存评论失败: {e}")
                continue
        
        # 提交事务
        conn.commit()
        print(f"成功保存 {success_count} 条评论到数据库")
        
        # 如果是在函数内创建的连接，需要关闭
        if close_conn:
            cursor.close()
            conn.close()
            
        return success_count
        
    except Exception as e:
        print(f"保存评论到数据库失败: {e}")
        return 0

# 程序入口点
if __name__ == "__main__":
    print("豆瓣电影Top250爬虫开始运行...")

    base_url = "https://movie.douban.com/top250"
    # 分页爬取（默认10页，每页最多25部电影）
    try:
        # 先爬取第一页
        crawl_page(base_url, 0)
        
        # 如果需要爬取所有页面，可以取消下面注释
        # for page in range(1, 10):
        #     page_url = f"{base_url}?start={page*25}&filter="
        #     crawl_page(page_url, page)
        
        print("所有电影爬取完成！")
    except Exception as e:
        print(f"爬取过程出错: {e}")
