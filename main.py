from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from movie_db_query import get_candidates, get_movie_data
import os

MOVIE_DB_API = os.environ.get('MOVIE_DB_API')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SECRET_KEY'] = 'any-secret=key'
Bootstrap(app)
db = SQLAlchemy(app)


class Movies(db.Model):
    id = db.Column('movie_id', db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(600), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(600))
    img_url = db.Column(db.String(400), nullable=False)


db.create_all()


class EditForm(FlaskForm):
    rating = FloatField(label='Your Rating Out of 10, eg., 4.7', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')


class AddForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


def seed_data():
    # Call this function to seed the data base with two entries.
    # Only run this code with final two lines commented out. Would be better in a separate file. Alas.
    new_movie = Movies(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    new_movie2 = Movies(
        title="Shawshank Redemption",
        year=1995,
        description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        rating=7.3,
        ranking=1,
        review="Stephen King's story brought to the big screen with excitement and elegance.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    db.session.add(new_movie)
    db.session.add(new_movie2)
    db.session.commit()


@app.route("/")
def home():
    ordered_movies = db.session.query(Movies).order_by(desc(Movies.rating))
    n = 1
    for movie in ordered_movies:
        movie.ranking = n
        db.session.add(movie)
        n += 1
    db.session.commit()
    return render_template("index.html", movies=ordered_movies)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    edited_movie = db.session.query(Movies).filter_by(id=id).one()
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        new_rating = edit_form.rating.data
        new_review = edit_form.review.data
        edited_movie.rating = new_rating
        edited_movie.review = new_review
        db.session.add(edited_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=edit_form, movie=edited_movie)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = AddForm()
    if add_form.validate_on_submit():
        new_title = add_form.title.data
        movie_candidates = get_candidates(new_title)
        return render_template('select.html', options=movie_candidates)
    return render_template('add.html', form=add_form)


@app.route("/find")
def find_movie():
    # Query for details for new card that user selected, add to db, and redirect to edit on the newly created card
    movie_api_id = request.args.get("id")
    if movie_api_id:
        data = get_movie_data(movie_api_id)
        new_movie = Movies(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.flush()
        db.session.refresh(new_movie)
        new_id = new_movie.id
        db.session.commit()
        return redirect(url_for('edit', id=new_id))


@app.route("/delete/<int:id>")
def delete(id):
    # DELETE A RECORD BY ID
    movie_to_delete = Movies.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.after_request
def add_header(r):
    # Clears cache on chrome so it's easier to play with CSS
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    return r


if __name__ == '__main__':
    app.run(debug=True)
