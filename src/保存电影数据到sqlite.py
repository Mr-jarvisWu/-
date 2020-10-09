import urllib.request
from bs4 import BeautifulSoup
import re
import sqlite3
# 主函数
def main():
    baseurl = 'https://movie.douban.com/top250?start='
    # 爬取网页
    datalist = get_data(baseurl)
    save_db = '豆瓣电影Top250.db'
    # 保存数据
    save_data(save_db, datalist)

find_link = re.compile(r'<a href="(.*?)">')    # 创建影片详情链接模式对象, (.*?) 表示只提取括号里面的内容
find_img = re.compile(r'<img alt=.*class=.*src="(.*?)"')   # 创建影片图片的模式对象，只提取链接
find_title = re.compile(r'<span class="title">(.*)</span>') # 创建影片名称模式对象
find_content = re.compile('<p class="">(.*?)</p>', re.S)     # 创建影片相关内容的模式对象 re.S: 让换行符包含在字符中
find_grade = re.compile('<span class="rating_num" property="v:average">(.*)</span>')   # 创建影片评分模式对象
find_evaluation = re.compile('<span>(.*人评价)</span>')    # 创建影片评价人数模式对象
find_details = re.compile('<span class="inq">(.*)</span>')   # 创建影片详情模式对象
# 爬取网页
def ask_url(url):
    html = ''
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=header)
        response = urllib.request.urlopen(req, timeout=5)
        html = response.read().decode('utf-8')
        # return html
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html

# 获取数据
def get_data(baseurl):
    datalist = []
    for i in range(10):    # 调用获取页面信息的函数10次
        url = baseurl + str(i*25)
        html = ask_url(url)    # 保存获取到的网页源代码
        # print(html)

    # 2. 逐步解析数据
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('div', class_='item'):    # 查找符合要求的字符串，遍历
            # print(item)     # 测试：查看电影 item 的全部信息
            data = []     # 保存一部电影的全部信息
            item = str(item)
            # 影片详情的链接
            link = re.findall(find_link, item)[0]        # 查找所有 item 中链接的模式对象
            data.append(link)
            img = re.findall(find_img, item)[0]
            data.append(img)
            title = re.findall(find_title, item)
            if len(title) > 1:
                chinese_title = title[0]
                data.append(chinese_title)
                other_title = title[1].replace('\\', ' ')
                other_title = title[1].replace('/', ' ')
                data.append(other_title)
            else:
                chinese_title = title[0]
                data.append(chinese_title)
                other_title = ' '
                data.append(other_title)
            grade = re.findall(find_grade, item)[0]
            data.append(grade)
            evaluation = re.findall(find_evaluation, item)[0]
            data.append(evaluation)
            details = re.findall(find_details, item)
            if len(details) == 1:
                data.append(details[0])
            else:
               data.append(' ')
            content = re.findall(find_content, item)[0]
            content = re.sub('<br(\s+)?/>(\s+)?', '', content)   # 将<br/>空格替换，可能有多个<br/>,因此用正则表达式，\s为匹配空白
            data.append(content.strip())       # strip()是字符串方法，去除字符串前后的空格

            datalist.append(data)
        # print(datalist)
    return datalist

def create_table(save_db):
    sql = '''
        create table movie
        (
        id integer primary key autoincrement,
        info_link message_text ,
        pic_link message_text ,
        cname varchar,
        ename varchar,
        grade numeric,
        evaluation varchar,
        details message_text,
        content message_text 
        )
    '''
    conn = sqlite3.connect(save_db)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

def save_data(save_db, datalist):
    create_table(save_db)
    for data in datalist:
        for index in range(len(data)):
            if index==4:
                continue
            else:
                data[index] = '"' + data[index] + '"'
        sql = '''insert into movie
            (info_link, pic_link, cname, ename, grade, evaluation, details, content)
            values({})'''.format(",".join(data))  # join: 将一个包含多个字符串的可迭代对象，转化为用分隔符连接的字符串
        conn = sqlite3.connect(save_db)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()

if __name__ == '__main__':
    main()