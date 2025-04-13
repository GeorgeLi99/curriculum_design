# 豆瓣电影爬虫项目 (Douban Movie Web Crawler)

## 项目简介

本项目是一个用于爬取豆瓣Top250电影信息的Python程序。它能够提取电影的详细信息，包括标题、年份、评分、评论数、导演、演员、类型等，并将这些信息保存到MySQL数据库中。此外，它还能爬取电影的评论内容。

## 功能特点

- 爬取豆瓣Top250电影列表
- 提取电影详细元数据，包括导演、编剧、演员、类型等
- 提取电影短评内容及评分
- 支持随机代理IP访问，避免被反爬虫系统拦截
- 防止被封禁的延时机制
- 将数据保存到MySQL数据库

## 环境要求

- Python 3.8+
- MySQL 5.7+ / 8.0+

## 依赖包

- **网络请求**
  - requests: 2.31.0
  - httpx: 0.24.1
- **HTML解析**
  - beautifulsoup4: 4.12.2
  - lxml: 4.9.3
  - pyquery: 2.0.0
- **数据处理**
  - pandas: 2.0.3
  - pymysql: 1.1.0
  - pymongo: 4.5.0
- **反爬处理**
  - fake-useragent: 1.1.3
  - python-dotenv: 1.0.0
- **并发控制**
  - aiohttp: 3.8.5
  - asyncio: 3.8.5
- **其他工具**
  - tqdm: 4.65.0
  - loguru: 0.7.0

## 安装方式

1. 克隆项目代码（或下载代码包）

   ```bash
   git clone https://github.com/GeorgeLi99/curriculum_design.git
   cd douban-crawler
   ```

2. 安装依赖包

   ```bash
   pip install -r requirements.txt
   ```

   - 其中`requirements.txt`文件列出了所有需要的依赖包，你无需一个个安装。
3. 安装MySQL数据库

   - 可以从MySQL官方网站下载安装包：
   - https://dev.mysql.com/downloads/mysql/

4. 准备MySQL数据库

   ```sql
   CREATE DATABASE douban DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

   - 其中`douban`是数据库名称，`utf8mb4`是字符集，`utf8mb4_unicode_ci`是排序规则。
   - 最好在创建完数据库后，顺带创建`movies`和`comments`表，以下是创建表的SQL语句:

   ```sql
   CREATE TABLE movies (
       id INT AUTO_INCREMENT PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       year VARCHAR(4) NOT NULL,
       rating DECIMAL(3,1) NOT NULL,
       comments_num INT NOT NULL,
       director VARCHAR(255) NOT NULL,
       script VARCHAR(255) NOT NULL,
       actors VARCHAR(255) NOT NULL,
       types VARCHAR(255) NOT NULL,
       country VARCHAR(255) NOT NULL,
       language VARCHAR(255) NOT NULL,
       release_date VARCHAR(255) NOT NULL,
       runtime VARCHAR(255) NOT NULL,
       aka VARCHAR(255) NOT NULL,
       imdb VARCHAR(255) NOT NULL
   );
   CREATE TABLE comments (
       id INT AUTO_INCREMENT PRIMARY KEY,
       movie_id INT NOT NULL,
       comment TEXT NOT NULL,
       star VARCHAR(255) NOT NULL,
       comment_time VARCHAR(255) NOT NULL,
       comment_person VARCHAR(255) NOT NULL,
       comment_vote VARCHAR(255) NOT NULL
   );
   ```

   - 当然，以上功能在`crawler.py`中已经实现，自己创建是为了以防万一。

## 配置说明

编辑`config.py`文件，配置数据库连接参数和爬虫设置：

```python
# 数据库连接信息
PASSWORD='your_password'  # 数据库密码，以你自己的数据库密码替换，请勿泄露作者的密码
DATABASE='douban'         # 数据库名称
USER='root'               # 数据库用户名
HOST='localhost'          # 数据库主机

# 爬虫设置
START_TIME=1  # 最小延时秒数
END_TIME=2    # 最大延时秒数
NUM_DASH=130  # 输出分隔线长度，次要
```

## 运行方式

直接运行`crawler.py`文件即可爬取豆瓣Top250电影信息：

```bash
python crawler.py
```

## 数据库结构

项目会创建两个数据表：

1. **movies表** - 存储电影基本信息
   - id: 自增主键
   - title: 电影标题
   - year: 年份
   - rating: 评分
   - comments_num: 评论数量
   - comments: 评论内容
   - director: 导演
   - script: 编剧
   - actors: 演员
   - types: 类型
   - country: 国家
   - language: 语言
   - release_date: 上映日期
   - runtime: 片长
   - aka: 别名
   - imdb: IMDb编号

2. **comments表** - 存储电影评论
   - id: 自增主键
   - movie_id: 关联电影ID
   - comment_text: 评论内容
   - comment_star: 评分
   - comment_time: 评论时间
   - comment_person: 评论人
   - comment_vote: 评论有用数

## 注意事项

- 程序运行时会随机选择IP代理，确保`ip.txt`文件中有可用的代理IP
- 你可以自己从网上搜集任意个IP地址，复制到`ip.txt`文件中，确保每行一个，格式如下：

```text
1.2.3.4:8080
5.6.7.8:8888
```

- 请合理设置爬取延时，防止被豆瓣封禁
- 在跑爬虫前请先确保数据库配置正确
- 尊重豆瓣的`robots.txt`规则，避免频繁爬取
- 请勿泄露作者的密码

## 联系方式

如有问题或建议，请提交Issue或联系：

- 邮箱：`241503030@smail.nju.edu.cn`
