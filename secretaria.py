from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

values = []
choices = []

class AddProfessorForm(Form):
	name = StringField('Nome', [validators.Length(min = 1, max = 100)])
	username = StringField('Nome de Usuário', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Senha', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'As senhas informadas não coincidem')
	])
	confirm = PasswordField('Confirme senha')
	prof = 3
	phone = StringField('Número de Telefone', [validators.Length(min = 1, max = 100)])

class DeleteSecretariaForm(Form):
	username = SelectField(u'Escolha qual você deseja excluir', choices=choices)

def add(mysql):
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	cur.close()
	form = AddProfessorForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		phone = form.phone.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, profile, phone) VALUES(%s, %s, %s, %s, %s)", (name, username, password, 2,phone))
		cur.execute("INSERT INTO secretaria(username) VALUES(%s)", [username])
		mysql.connection.commit()
		cur.close()
		flash('Secretaria adicionada', 'success')
		return redirect(url_for('admin_dash'))
	return render_template('add_secretaria.html', form=form)


def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM secretaria")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	if len(choices)==1:
		flash('Secretaria não pode ser removida porque é única', 'danger')
		return redirect(url_for('admin_dash'))
	form = DeleteSecretariaForm(request.form)
	if request.method == 'POST':
		username = form.username.data
		cur.execute("DELETE FROM secretaria WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Secretaria removida', 'success')
		return redirect(url_for('admin_dash'))
	return render_template('delete_secretaria.html', form = form)
