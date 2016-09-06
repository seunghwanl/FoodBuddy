from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, EqualTo, Length

class LoginForm(Form):
    username = StringField('Username: ', validators=[Required()])
    passwd = PasswordField('Password: ', validators=[Required()])
    submit = SubmitField('Login')

class RegistrationForm(Form):
    username = StringField('Username: ', validators=[Required(), Length(min = 4, max = 20,
        message='Username length between 4 and 20 required')])
    passwd = PasswordField('Password: ', validators=[Required(), Length(min = 8, max = 20,
        message=' password length between 8 and 20 required')])
    passwd_confirm = PasswordField('Confirm Password: ', validators=[Required(), EqualTo('passwd',
        message='Passwords mismatch. Retype passwords please.')] )
    submit = SubmitField('Register')


class SearchForm(Form):
    search = StringField('Menu: ', validators=[Required()])
    submit = SubmitField('Search')