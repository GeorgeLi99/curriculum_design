# -*- coding: utf-8 -*-

import requests
import httpx
import bs4
import re
import pymysql
import random
import time
from urllib.parse import urljoin
from config import *

class Movie:
    def __init__(self, number, title, year, rating, comments_num, weight, similar, director, script, actors, types, 
                 country=None, language=None, release_date=None, runtime=None, aka=None, imdb=None, comments=None, official_site=None):
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
        # 官方网站
        self.official_site = official_site

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

def get_ip():
    """从配置的代理IP文件中获取随机代理"""
    ip_list=[]
    with open(PROXY_FILE, 'r') as file:
        ip_list=file.readlines()
    proxy=ip_list[random.randint(0,len(ip_list)-1)]
    proxy=proxy.replace('\r\n','').replace('\n', '')
    proxies={
        'http':'http://'+str(proxy),
        # 'https':'https://'+str(proxy)
    }   
    print(proxies)
    return proxies  # request 的ip代理约定格式

# 使用随机 IP、可选延时请求页面
def request_with_random_ip(url, referer=None, min_delay=REQUEST_MIN_DELAY, max_delay=REQUEST_MAX_DELAY, headers=None):
    '''
    使用随机代理、可选延时请求页面
    Args:
        url (str): 目标URL
        referer (str): 可选，Referer头
        min_delay/max_delay: 随机延时区间（秒）
        headers (dict): 可选自定义请求头
    Returns:
        requests.Response | None
    '''
    req_headers = HEADERS.copy() if headers is None else headers
    if referer:
        req_headers['Referer'] = referer
    proxy = get_ip()
    # 延时参数优先使用传参，否则用配置文件
    delay = random.uniform(min_delay, max_delay)
    try:
        res = requests.get(url, headers=req_headers, proxies=proxy, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL)
        print(f"请求 {url}，状态码: {res.status_code}，延时 {delay:.2f}s")
        time.sleep(delay)
        if res.status_code == 200:
            return res
        else:
            print(f"请求失败: 状态码 {res.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def request_with_random_ip(url, headers=None):
    """使用随机代理IP发送HTTP请求
    
    Args:
        url (str): 要请求的URL
        
    Returns:
        requests.Response: 请求响应对象，如果请求失败则返回None
    """
    # 使用config中的请求头配置
    headers = HEADERS

    # 每次请求前随机选择新的IP代理
    proxy = get_ip()
    print(f"使用代理: {proxy}")
    
    try:
        # 发起请求，使用config中的超时和验证设置
        res = requests.get(url, headers=headers, proxies=proxy, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL)
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
        
        # 提取官方网站（如有）
        official_site = None
        if info_div:
            # 查找所有 <a> 标签，rel=nofollow, target=_blank
            official_links = info_div.find_all('a', attrs={'rel': 'nofollow', 'target': '_blank'})
            if official_links:
                # 取第一个外链地址
                official_site = official_links[0].get('href')

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
        if official_site:
            print(f"官方网站: {official_site}")
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
        print("-" * NUM_DASH)  # 添加分隔线

        # 传入当前电影ID和电影页面对象
        comment_objects = crawl_comment(number, movie_soup, movie_url)
        if comment_objects:
            print(f"共获取了 {len(comment_objects)} 条评论")
        else:
            print("未获取到评论")

        # 返回完整的实现可以返回电影对象
        return Movie(number, title, year, rating, comments_num, weight, similar, director, script, actors, types,
                     country, language, release_date, runtime, aka, imdb, comment_objects, official_site)

    except Exception as e:
        print(f"解析电影信息失败: {e}")
        return None

def crawl_comment(movie_id, movie_soup, movie_url):
    count=0
    try:
        # 获取评论链接
        comments_section = movie_soup.find('div', attrs={'id':'comments-section'})
        if not comments_section:
            print(f"未找到评论区域")
            return []
            
        mod_comments = comments_section.find('div', attrs={'class':'mod-hd'})
        if not mod_comments:
            print(f"未找到评论区域")
            return []
            
        comment_link_area = mod_comments.find('span', attrs={'class':'pl'})
        if not comment_link_area:
            print(f"未找到评论链接")
            return []

        comment_link = comment_link_area.find('a', attrs={'href':True})
        if not comment_link:
            print(f"未找到评论链接")
            return []
            
        relative_comment_url = comment_link['href']
        
        # 确保URL以http开头
        comment_url = f"http://{relative_comment_url}" if not relative_comment_url.startswith('http') else relative_comment_url
        
        print(f"访问评论页面: {comment_url}")
        detail_request = request_with_random_ip(comment_url)
    except Exception as e:
        print(f"构建评论页面URL失败: {e}")
        return []
    if detail_request:
        comment_soup=bs4.BeautifulSoup(detail_request.text,'html.parser')
        comments=comment_soup.find_all('div',attrs={'class':'comment-item','data-cid':True})
        
        # 获取所有评论，但只打印第一个
        comment_objects = []
        for comment in comments:
            comment_object = get_comment_info(comment, movie_id)
            comment_objects.append(comment_object)
            count+=1
        
        # 分页爬取评论
        while(count < 60):
            try:
                # 获取评论页面
                comment_base=comment_soup.find('div', attrs={'id':'comments','class':'mod-bd'})
                if not comment_base:
                    print(f"未找到评论区域")
                    break

                # 获取分页器
                paginator = comment_base.find('div', attrs={'id':'paginator', 'class':'center'})
                if not paginator:
                    print(f"没有找到分页器，停止获取更多评论")
                    break
                
                # 尝试获取下一页链接
                next_link = paginator.find('a', attrs={'href':True, 'data-page':'next', 'class':'next'})
                if not next_link:
                    print(f"没有下一页链接，已到最后一页")
                    break
                
                relative_next_url = next_link['href']
                
                # 处理JavaScript链接
                if relative_next_url.startswith('javascript:'):
                    print(f"下一页使用JavaScript处理，停止爬取")
                    break
                
                # 处理URL拼接
                next_url_without_http = urljoin(comment_url, relative_next_url)
                
                # 确保URL以http开头
                next_url = f"http://{next_url_without_http}" if not next_url_without_http.startswith('http') else next_url_without_http
                
                print(f"访问下一页评论: {next_url}")
                # 添加随机延时，避免请求过快
                time.sleep(random.randint(START_TIME, END_TIME))
                
                detail_request = request_with_random_ip(next_url)
                if detail_request:
                    comment_soup = bs4.BeautifulSoup(detail_request.text, 'html.parser')
                    comments = comment_soup.find_all('div', attrs={'class':'comment-item', 'data-cid':True})
                    
                    # 如果没有评论，停止爬取
                    if not comments:
                        print(f"没有找到评论，停止爬取")
                        break
                    
                    # 取得那一页的评论 URL，更新 comment_url 为当前页
                    comment_url = next_url
                    
                    # 获取评论
                    for comment in comments:
                        comment_object = get_comment_info(comment, movie_id)
                        comment_objects.append(comment_object)
                        count += 1
                        if count >= 60:  # 到达最大数量，停止爬取
                            break
                    
                    # 如果已达到最大评论数量，退出循环
                    if count >= 60:
                        break
                else:
                    print(f"访问下一页评论失败，停止爬取")
                    break
            except Exception as e:
                print(f"分页爬取异常: {e}")
                break
                    
        # 打印第一个评论
        if comment_objects and len(comment_objects) > 0:
            print(f"共获取了 {len(comment_objects)} 条评论，显示第一条：")
            print(f"评论人: {comment_objects[0].comment_person}")
            print(f"评论内容: {comment_objects[0].comment}")
            print(f"评论星级: {comment_objects[0].star}")
            print(f"评论时间: {comment_objects[0].comment_time}")
            print(f"评论票数: {comment_objects[0].comment_vote}")
            print("-" * NUM_DASH)  # 添加分隔线
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
        soup = bs4.BeautifulSoup(res.text, PARSER)
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
            imdb VARCHAR(20),
            official_site VARCHAR(255)
        )
        ''')
        
        # 提交电影表创建事务
        conn.commit()
        print("成功创建 movies 表并保存电影数据")
        
        # 创建评论表 - 尝试删除并重新创建如果已存在
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id INT NOT NULL,           -- 关联到电影表
            comment_text TEXT NOT NULL,      -- 评论内容
            comment_star VARCHAR(20),       -- 评分
            comment_time VARCHAR(50),        -- 评论时间
            comment_person VARCHAR(100),     -- 评论人
            comment_vote INT                 -- 评论有用数
        )
        ''')
        conn.commit()
        print("成功创建 comments 表并保存评论数据")

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
                      types, country, language, release_date, runtime, aka, imdb, official_site) 
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # 检查是否是评论对象列表，如果是，使用空字符串
        comments_text = ""
        if isinstance(movie.comments, list):
            # 如果是评论对象列表，后面会单独保存到comments表
            print("评论内容作为对象列表处理，将单独保存")
        elif movie.comments is not None:
            # 如果是文本，直接使用
            comments_text = str(movie.comments)
            
        cursor.execute(sql, (
            movie.title, 
            movie.year, 
            movie.rating, 
            movie.comments_num,
            comments_text,  # 确保这里存入的是文本而不是对象列表
            directors_str,
            script_str,
            actors_str,
            types_str,
            country_str,
            language_str,
            release_date_str,
            movie.runtime,
            aka_str,
            movie.imdb,
            movie.official_site
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
                vote = int(comment.comment_vote) if comment.comment_vote else 0
            
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
def main():
    """程序主入口函数，控制爬虫流程"""
    print("豆瓣电影Top250爬虫开始运行...")

    # 分页爬取（使用config配置的页数）
    try:
        # 先爬取第一页
        crawl_page(BASE_URL, 0)
        
        # 如果需要爬取多页，根据配置的MAX_PAGES决定
        if MAX_PAGES > 1:
            for page in range(1, MAX_PAGES):
                page_url = f"{BASE_URL}?start={page*25}&filter="
                crawl_page(page_url, page)
        
        print("所有电影爬取完成！")
    except Exception as e:
        print(f"爬取过程出错: {e}")

if __name__ == "__main__":
    main()
