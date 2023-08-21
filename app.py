import os
import uuid

from flask import Flask, render_template, flash, request, redirect, url_for
from flask_ckeditor import CKEditor
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import date

# from sqlalchemy.testing.plugin.plugin_base import post
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from webforms import NamerForm, PasswordForm, UserForm, PostForm, LoginForm, SearchForm

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# db = SQLAlchemy(app)
# migrate = Migrate(app, db, render_as_batch=True)

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# JSON
@app.route('/date')
def get_current_date():
    return {'Date': date.today()}


@app.route('/admin')
@login_required
def admin():
    if current_user.id == 3:
        flash('Wellcome admin')
        return render_template('admin.html')
    else:
        flash('Sorry yoy are not admin')
        return render_template(url_for('index'))


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
            user = Users(username=form.username.data,
                         name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.created)
    return render_template('add_user.html',
                           form=form,
                           name=name,
                           our_users=our_users,)


@app.route('/update_user/<int:id>', methods=['POST', 'GET'])
@login_required
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update_user.html",
                                   form=form,
                                   name_to_update=name_to_update, id=id)
        except:
            flash("Error!  Looks like there was a problem...try again!")
            return render_template("update_user.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        return render_template("update_user.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User Deleted!')
            return redirect(url_for('add_user'))
        except:
            flash('Deleting Error')
            return redirect(url_for('add_user'))
    else:
        flash('permission denied')
        return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash('login success!')
                return redirect(url_for('dashboard'))
            else:
                flash('wrong password')
        else:
            flash('User not exist')

    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('you logout')
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/detail_post/<int:id>')
def detail_post(id):
    post = Posts.query.get_or_404(id)
    return render_template('detail_post.html', post=post)


@app.route('/add_post', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     poster_id=poster,
                     slug=form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash('OK')
        return redirect(url_for('blog_posts'))

    return render_template('add_post.html', form=form,)


# @app.route('/edit_post/<int:id>', methods=['POST', 'GET'])
# @login_required
# def edit_post(id):
#     editing_post = Posts.query.get_or_404(id)
#     form = PostForm()
#     if current_user.id == editing_post.poster.id:
#
#         if form.validate_on_submit():
#             editing_post.title = form.title.data
#             editing_post.slug = form.slug.data
#             editing_post.content = form.content.data
#
#             db.session.add(editing_post)
#             db.session.commit()
#             flash('ok')
#             return redirect(url_for('post', id=editing_post.id))
#
#         return render_template('edit_post.html',
#                                form=form, editing_post=editing_post)
#     else:
#         flash('Permission Denied')
#         return redirect(url_for('blog_posts'))


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('blog_posts'))

    if current_user.id == post.poster_id or current_user.id == 14:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post...")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("blog_posts.html", posts=posts)


@app.route('/blog_posts')
def blog_posts():
    posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template('blog_posts.html', posts=posts)


@app.route('/delete_post/<int:id>')
def delete_post(id):
    post = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post.poster.id:

        try:
            db.session.delete(post)
            db.session.commit()
            flash('Delete ok')
            return redirect(url_for('blog_posts'))
        except:
            flash('Delete error')
            return redirect(url_for('blog_posts'))
    else:
        flash('Permission Denied')
        return redirect(url_for('blog_posts'))


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']

        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + '_' + pic_filename

            saver = request.files['profile_pic']
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User Updated Successfully!')
                return render_template('dashboard.html',
                                       form=form,
                                       name_to_update=name_to_update, )
            except:
                flash('Error Updating!')
                return render_template('dashboard.html',
                                       form=form,
                                       name_to_update=name_to_update, )
        else:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template('dashboard.html',
                                   form=form,
                                   name_to_update=name_to_update, )

    else:
        return render_template('dashboard.html',
                               form=form,
                               name_to_update=name_to_update, )


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post_searched = form.searched.data
        posts = posts.filter(Posts.title.like('%' + post_searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html',
                               form=form,
                               searched=post_searched,
                               posts=posts)
    else:
        flash('Error Validation!')
        return render_template('search.html')


# MODELS
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120), default='Red')
    # about_author = db.Column(db.String(500), nullable=True)
    about_author = db.Column(db.Text(500), nullable=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    posts = db.relationship('Posts', backref='poster')


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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


if __name__ == '__main__':
    app.run()
