from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField

class EditForm(Form):
    name = StringField('Nome', [validators.Length(min=1, max=60)])
    phone = StringField('Número de Telefone', [validators.Length(min = 1, max = 100)])