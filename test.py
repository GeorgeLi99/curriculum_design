from bs4 import BeautifulSoup

# 打开HTML文件
with open('baidu.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# 创建BeautifulSoup对象解析HTML内容
bs = BeautifulSoup(html_content, "html.parser")

# 缩进格式
print(bs.prettify()) 

# 获取title标签的所有内容
print(bs.title) 

# 获取title标签的名称
print(bs.title.name) 

# 获取title标签的文本内容
print(bs.title.string) 

# 获取head标签的所有内容
print(bs.head) 

# 获取第一个div标签中的所有内容
print(bs.div) 

# 获取第一个div标签的id的值
print(bs.div["id"])

# 获取第一个a标签中的所有内容
print(bs.a) 

# 获取所有的a标签中的所有内容
print(bs.find_all("a"))

# 获取id="u1"
print(bs.find(id="u1")) 

# 获取所有的a标签，并遍历打印a标签中的href的值
for item in bs.find_all("a"): 
	print(item.get("href")) 
	
# 获取所有的a标签，并遍历打印a标签的文本值
for item in bs.find_all("a"): 
	print(item.get_text())

