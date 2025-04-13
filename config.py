# 数据库配置
PASSWORD='54Tt9986'
DATABASE='douban'
USER='root'
HOST='localhost'

# 爬虫延时设置（秒）
START_TIME=1
END_TIME=2

# 显示格式
NUM_DASH=130

# 网络请求配置
REQUEST_TIMEOUT=15
VERIFY_SSL=False
PARSER='html.parser'

# 爬虫范围配置
MAX_PAGES=1  # 爬取页数，设为10可爬取全部250部电影
MAX_COMMENTS_PER_MOVIE=60  # 每部电影最多爬取的评论数

# 请求头配置
HEADERS = {
    'Host':'movie.douban.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'cookie':'bid=uVCOdCZRTrM; douban-fav-remind=1; __utmz=30149280.1603808051.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __gads=ID=7ca757265e2366c5-22ded2176ac40059:T=1603808052:RT=1603808052:S=ALNI_MYZsGZJ8XXb1oU4zxzpMzGdK61LFA; _pk_ses.100001.4cf6=*; __utma=30149280.1867171825.1603588354.1603808051.1612839506.3; __utmc=30149280; __utmb=223695111.0.10.1612839506; __utma=223695111.788421403.1612839506.1612839506.1612839506.1; __utmz=223695111.1612839506.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=223695111; ap_v=0,6.0; __utmt=1; dbcl2="165593539:LvLaPIrgug0"; ck=ZbYm; push_noty_num=0; push_doumail_num=0; __utmv=30149280.16559; __utmb=30149280.6.10.1612839506; _pk_id.100001.4cf6=e2e8bde436a03ad7.1612839506.1.1612842801.1612839506.',
    'accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
}

# URL配置
BASE_URL = 'https://movie.douban.com/top250'
COMMENT_URL_TEMPLATE = '{}/comments?start={}&limit=20&sort=new_score&status=P'

# 代理设置
PROXY_FILE = 'ip.txt'