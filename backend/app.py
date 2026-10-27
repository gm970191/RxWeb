from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 初始化数据库
def init_db():
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, image TEXT, parameters TEXT, description TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, type TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS resources (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, url TEXT)')
        conn.commit()

# 填充模拟数据
def populate_data():
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        # 产品数据
        products = [
            ('产品1', '分类1', 'image1.jpg', '参数1', '产品1详细描述'),
            ('产品2', '分类2', 'image2.jpg', '参数2', '产品2详细描述'),
            ('产品3', '分类1', 'image3.jpg', '参数3', '产品3详细描述'),
            ('产品4', '分类2', 'image4.jpg', '参数4', '产品4详细描述'),
            ('产品5', '分类3', 'image5.jpg', '参数5', '产品5详细描述')
        ]
        c.executemany('INSERT INTO products (name, category, image, parameters, description) VALUES (?,?,?,?,?)', products)
        # 新闻数据
        news = [
            ('30周年庆典', '公司举办30周年庆典活动', '公司新闻'),
            ('新产品发布', '我们发布了一款新产品', '产品新闻'),
            ('行业峰会参与', '公司代表参加行业峰会', '行业新闻'),
            ('技术研讨会', '举办内部技术研讨会', '技术新闻'),
            ('合作伙伴签约', '与新伙伴达成合作协议', '合作新闻')
        ]
        c.executemany('INSERT INTO news (title, content, type) VALUES (?,?,?)', news)
        # 资源数据
        resources = [
            ('文档1', '文档', 'doc1.pdf'),
            ('视频1', '视频', 'video1.mp4'),
            ('白皮书', '文档', 'whitepaper.pdf'),
            ('演示视频', '视频', 'demo_video.mp4'),
            ('技术报告', '文档', 'tech_report.pdf')
        ]
        c.executemany('INSERT INTO resources (name, type, url) VALUES (?,?,?)', resources)
        conn.commit()

@app.route('/')
def index():
    return jsonify({'message': '主页暂未实现，请使用前端服务访问'})

@app.route('/products')
def get_products():
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM products')
        products = c.fetchall()
    columns = [description[0] for description in c.description]
    product_list = [dict(zip(columns, product)) for product in products]
    return jsonify(product_list)

@app.route('/news')
def get_news():
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM news')
        news = c.fetchall()
    columns = [description[0] for description in c.description]
    news_list = [dict(zip(columns, item)) for item in news]
    return jsonify(news_list)

@app.route('/resources')
def get_resources():
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM resources')
        resources = c.fetchall()
    columns = [description[0] for description in c.description]
    resource_list = [dict(zip(columns, item)) for item in resources]
    return jsonify(resource_list)

@app.route('/products/<int:id>')
def get_product_detail(id):
    with sqlite3.connect('../company.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM products WHERE id = ?', (id,))
        product = c.fetchone()
        if product:
            columns = [description[0] for description in c.description]
            product_dict = dict(zip(columns, product))
            return jsonify(product_dict)
        else:
            return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    init_db()
    populate_data()
    app.run(debug=True)