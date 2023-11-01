from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)  # создаём объект на основе класса скьюэл алхимия и передаём туда объект нашего фласка


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # nullable фолс означает что это поле не может бытьь пустым
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    # intro = db.Column(db.String(300), nullable=False)
    # date = db.Column(db.DateTime, default=datetime.utcnow)  # время и дата когда мы добавляем статью
    def __repr__(self):
        return self.title  # выдаём сам объект и его id   '<Item %r>' % self.id


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html',data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,  # id компании
              secret_key='test')  # секретный ключик компании(при регистрации на платёжной системе FONDY)
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(item.price)+"00"
    }
    url = checkout.url(data).get('checkout_url')  # ссылка на оплату
    return redirect(url)

# @app.route('/detail/<int:id>')  # страничка для детального рассмотрения конкретной статьи
# def post_detail(id):
#     article = Item.query.get(id)  # получаем определённый объект по его id
#     return render_template("detail.html", article=article)  # "About Flask page"
#
#
# @app.route('/detail/<int:id>/delete')  # страничка для удаления конкретной статьи
# def post_delete(id):
#     article = Item.query.get_or_404(id)  # если не будет найдена запись по id, то будет вызвана ошибка 404
#
#     try:
#         db.session.delete(article)
#         db.session.commit()
#         return redirect('/')
#     except:
#         return "При удалении статьи возникла ошибка"


@app.route('/create', methods=['POST', 'GET'])  # создаём главную страничку для публикации статьи
# через декоратор, post & get указываем, чтобы получать ответ
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']

        item = Item(title=title, price=price, text=text)

        try:
            db.session.add(item)  # добавляем в бд
            db.session.commit()  # сохраняем в бд
            return redirect('/')
        except:
            return "При добавлении товара возникла ошибка"
    else:
        return render_template('create.html')  # для публикации статьи


# БД - Таблицы - Записи
# таблица:
#   id  title   price   Actual
#   1   Cat1    1000$   True
#   2   Cat2    2000$   False

if __name__ == "__main__":
    app.run()
