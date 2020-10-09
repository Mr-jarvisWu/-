from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def home():
    return index()

@app.route('/movie')
def movie():
    movies = []
    conn = sqlite3.connect('豆瓣电影Top250.db')
    cur = conn.cursor()
    sql = '''select * from movie'''
    cur = cur.execute(sql)
    for item in cur:
        movies.append(item)
    conn.close()
    return render_template('movie.html', movies=movies)

@app.route('/score')
def score():
    grade = []   # 电影评分的列表
    num = []   # 电影数量的列表
    conn = sqlite3.connect('豆瓣电影Top250.db')
    cur = conn.cursor()
    sql = '''select grade,count(grade) from movie group by grade'''
    cur = cur.execute(sql)
    for item in cur:
        grade.append(str(item[0]))
        num.append(item[1])
    conn.close()
    return render_template('score.html', grade=grade, num=num)

@app.route('/words')
def words():
    return render_template('words.html')

@app.route('/team')
def team():
    return render_template('team.html')





if __name__ == '__main__':
    app.run()
