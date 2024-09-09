from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

class CreateUserForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])

class LoginForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    
    title = StringField("Title", validators=[InputRequired()])
    content = StringField("Content", validators=[InputRequired()])