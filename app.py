from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# MODELS
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120), default='Red')
    created = db.Column(db.DateTime, default=datetime.utcnow)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f'{self.name}'


# FORMS
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password',
                                  validators=[DataRequired(),
                                              EqualTo('password_hash2', message='Password Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What's your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    content = StringField("content", validators=[DataRequired()])
    author = StringField("author", validators=[DataRequired()])
    slug = StringField("slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash(f'Flash message {name}', category='message')
    return render_template('name.html', name=name, form=form)


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        pw_to_check = Users.query.filter_by(email=email).first()

        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html',
                           email=email,
                           password=password,
                           form=form,
                           passed=passed,
                           pw_to_check=pw_to_check,)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    # email = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.created)
    return render_template('add_user.html',
                           form=form,
                           name=name,
                           our_users=our_users,)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     author=form.author.data,
                     slug=form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash('OK')
        return redirect('/')

    return render_template('add_post.html', form=form,)


@app.route('/edit_post/<int:id>', methods=['POST', 'GET'])
def edit_post(id):
    form = PostForm()
    editing_post = Posts.query.get_or_404(id)
    if form.validate_on_submit():
        editing_post.title = form.title.data
        editing_post.author = form.author.data
        editing_post.slug = form.slug.data
        editing_post.content = form.content.data

        db.session.commit()
        flash('ok')
        return redirect(url_for('post', id=editing_post.id))

    return render_template('edit_post.html',
                           form=form, editing_post=editing_post)


@app.route('/update_record/<int:id>', methods=['POST', 'GET'])
def update_record(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template('update_record.html',
                                   form=form,
                                   name_to_update=name_to_update,)
        except:
            flash('Error Updating!')
            return render_template('update_record.html',
                                   form=form,
                                   name_to_update=name_to_update, )

    else:
        return render_template('update_record.html',
                               form=form,
                               name_to_update=name_to_update,)


@app.route('/delete_record/<int:id>')
def delete_record(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted!')
        return redirect(url_for('add_user'))
    except:
        flash('Deleting Error')
        return redirect(url_for('add_user'))


# JSON
@app.route('/date')
def get_current_date():
    return {'Date': date.today()}


@app.route('/blog_posts')
def blog_posts():
    posts = Posts.query.all()
    return render_template('blog_posts.html', posts=posts)


@app.route('/delete_post/<int:id>')
def delete_post(id):
    post = Posts.query.get_or_404(id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Delete ok')
        return redirect(url_for('blog_posts'))
    except:
        flash('Delete error')
        return redirect(url_for('blog_posts'))


if __name__ == '__main__':
    app.run()
