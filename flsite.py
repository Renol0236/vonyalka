from flask import Flask, render_template, url_for, request, flash, redirect, session, abort, g
from db_scripts import FDataBase
from flask_login import LoginManager, login_user, login_required
from userlogin import UserLogin
import os
import sqlite3

DEBUG = True
DATABASE = 'tmp/flsite.db'

database = None

app = Flask(__name__)
app.config.from_object(__name__)

app.config['SECRET_KEY'] = 'invoker'

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, database)


@app.before_request
def before_request():
    global database
    db = get_db()
    database = FDataBase(db)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_request
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.route('/')
def main_page():
    print(database.getPostsAnonce())
    return render_template('main.html', title='MainPage', posts=database.getPostsAnonce())


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        user = database.getUser(request.form['username'])
        if user and request.form['password'] == user['password']:
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('main_page'))

    return render_template('login.html')


@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"Профиль пользователя: {username}"


@app.route("/regestration", methods=['POST', 'GET'])
def regestration():
    db = get_db()
    database = FDataBase(db)
    if request.method == "POST":
        if len(request.form['username']) >= 3 and len(request.form['password']) >= 8:
            if database.getSameUser(request.form['username']):
                res = database.addUser(request.form['username'], request.form['email'], request.form['password'])
                if not res:
                    flash('Ошибка при регстрации', category='error')
                else:
                    flash('Успешная регестрация', category='success')
                    return redirect(url_for('login'))
            else:
                if len(request.form['username']) <= 2:
                    flash('Слишком короткий логин', category='error')
                elif len(request.form['password']) <= 7:
                    flash('Слишком короткий пароль', category='error')
                else:
                    flash('Такой пользователь уже существует', category='error')

    return render_template('regestration.html')


@app.route('/add_post', methods=["POST", "GET"])
@login_required
def add_post():
    if request.method == "POST":
        if len(request.form['title']) >= 3 and len(request.form['description']) >= 5:
            res = database.addPost(request.form['title'], request.form['price'], request.form['description'],
                                   request.form['contact'])
            if not res:
                flash('Не удалось создать объявление', category='error')
            else:
                flash('Объявление создано успешно', category='success')
        else:
            flash('Объявление не соответсвует требованиям', category='error')

    return render_template('add_post.html', css='style_reg.css', title='Объявление')


@app.route('/post/<int:id_post>')
def showPost(id_post):
    title, text, price, contact = database.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html', title=title, text=text, price=price, contact=contact)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error404.html'), 404


@app.errorhandler(401)
def pageNotUathoraized(error):
    return render_template('error401.html'), 401


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
