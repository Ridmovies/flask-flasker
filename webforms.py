from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
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
    # author = StringField("author", validators=[DataRequired()])
    slug = StringField("slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password_hash = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Login")