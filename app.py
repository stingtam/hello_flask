import os
import sys

import click
from faker import Faker
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化扩展，传入程序实例 app
db = SQLAlchemy(app)


# 保存两类数据：1用户信息；2电影条目信息。
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    name = Faker().name()
    movies = [
        {"title": "My Neighbor Totoro", "year": "1988"},
        {"title": "Dead Poets Society", "year": "1989"},
        {"title": "A Perfect World", "year": "1993"},
        {"title": "Leon", "year": "1994"},
        {"title": "Mahjong", "year": "1996"},
        {"title": "Swallowtail Butterfly", "year": "1996"},
        {"title": "King of Comedy", "year": "1999"},
        {"title": "Devils on the Doorstep", "year": "1999"},
        {"title": "WALL-E", "year": "2008"},
        {"title": "The Pork of Music", "year": "2012"},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("Done.")


# 对于多个模板内都需要使用的变量，我们可以使用 app.context_processor 装饰器注册一个模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 等同于{user: user}


@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template("404.html"), 404


@app.route("/")
def index():
    # 不需要定义user
    # user = User.query.first()
    movies = Movie.query.all()
    # return render_template("index.html", user=user, movies=movies)
    # 删除参数user=user
    return render_template("index.html", movies=movies)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
