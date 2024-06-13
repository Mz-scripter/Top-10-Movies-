from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-10-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy()
db.init_app(app)
api_key = "c9c1c22a4c94d5a18f66e3128fa5651f"
Movie_db_url = "https://api.themoviedb.org/3/search/movie"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(115), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(115), nullable=False)

class EditForm(FlaskForm):
    rating = FloatField('Your rating out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

# with app.app_context():
#     db.create_all()
#     new_movie = Movie(title='Vampire Diaries', year=2009, description='On her first day at high school, Elena meets Stefan and immediately feels a connection with him. However, what she does not know is that Stefan and his brother, Damon, are in fact vampires.', rating=9.3, ranking=9, review='Damon was the best character.', img_url='https://i.pinimg.com/236x/c1/93/eb/c193eb3bd3eba322534a9aedf792b3bc.jpg')
#     db.session.add(new_movie)
#     db.session.commit()

@app.route("/", methods=["GET", "POST"])
def home():
    num = 0     
    with app.app_context():
        all_movies = db.session.query(Movie).order_by(Movie.rating.asc()).all()
        for i in range(len(all_movies)):
            all_movies[i].ranking = len(all_movies) - num
            num += 1
        db.session.commit()   
        return render_template("index.html", movies=all_movies)
        

@app.route("/select")
def select():
    movie_id = request.args.get('id')
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params={'api_key':api_key})
    movie_details = response.json()
    launch_date = datetime.fromisoformat(movie_details['release_date'])
    launch_year = launch_date.strftime("%Y")
    with app.app_context():
        new_movie = Movie(title=movie_details['original_title'], description=movie_details['overview'], img_url=f"https://image.tmdb.org/t/p/w185{movie_details['poster_path']}", year=launch_year)
        db.session.add(new_movie)
        movie = Movie.query.filter_by(title=movie_details['original_title']).first()
        db.session.commit()
        return redirect(url_for('edit', id=movie.id))

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    if request.method == "POST":
        movie_id = request.form['id']
        movie_to_update = db.session().query(Movie).get(movie_id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    return render_template("edit.html", movie=movie_selected, form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.session().query(Movie).get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        response = requests.get(Movie_db_url, params={"query":form.title.data, "api_key":api_key})
        response.raise_for_status()
        data = response.json()["results"]
        return render_template('select.html', movies=data)
    return render_template('add.html', form=form)



# with app.app_context():
#     movie_id = 3
#     movie_to_delete = Movie.query.get(movie_id)
#     db.session.delete(movie_to_delete)
#     db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
