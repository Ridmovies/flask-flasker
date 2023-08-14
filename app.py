from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# MODELS
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120), default='Red')
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.name}'


# FORMS
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What's your Name", validators=[DataRequired()])
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
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.created)
    return render_template('add_user.html',
                           form=form,
                           name=name,
                           our_users=our_users,)


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




if __name__ == '__main__':
    app.run()
