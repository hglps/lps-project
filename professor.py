from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt
from datetime import datetime
from wtforms.fields.html5 import DateField

values = []
choices = []

class AddProfessorForm(Form):
	name = StringField('Nome', [validators.Length(min = 1, max = 100)])
	username = StringField('Nome de Usuário', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Senha', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'As senhas informadas não coincidem')
	])
	confirm = PasswordField('Confirmar senha')
	prof = 3
	phone = StringField('Número de Telefone', [validators.Length(min = 1, max = 100)])

class professorForm(Form):
	name = RadioField('Selecionar nome de usuário', choices = choices)
	date = DateField('Data', format='%Y-%m-%d')
	report = StringField('Relatório', [validators.InputRequired()])
	rate = RadioField('Resultado', choices = [('bom', 'bom'),('medio', 'medio'),('baixo', 'baixo') ])

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
		prof = 2
		phone = form.phone.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, profile, phone) VALUES(%s, %s, %s, %s, %s)", (name, username, password, 3,phone))
		cur.execute("INSERT INTO professors(username) VALUES(%s)", [username])
		mysql.connection.commit()
		cur.close()
		flash('Novo professor adicinado', 'success')
		return redirect(url_for('admin_dash'))
	return render_template('add_professor.html', form=form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM professors")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = DeleteSecretariaForm(request.form)
	if len(choices)==1:
		flash('Professor(a) não pode ser removido(a) porque é único(a)', 'danger')
		return redirect(url_for('admin_dash'))
	if request.method == 'POST':
		username = form.username.data
		q = cur.execute("SELECT username FROM professors WHERE username != %s", [username])
		b = cur.fetchall()
		new = b[0]['username']
		cur.execute("UPDATE alunos SET professor = %s WHERE professor = %s", (new, username))
		cur.execute("DELETE FROM professors WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Professor(a) removido(a)', 'success')
		return redirect(url_for('admin_dash'))
	return render_template('delete_secretaria.html', form = form)

def openDash(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	cur.execute("SELECT name, count FROM livros")
	livros = cur.fetchall()
	cur.execute("SELECT username FROM alunos WHERE professor = %s", [session['username']])
	alunos_under = cur.fetchall()
	cur.close()
	cur = mysql.connection.cursor()

	q = cur.execute("SELECT username FROM alunos WHERE professor = %s", [session['username']])
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	cur.close()

	form = professorForm(request.form)

	if request.method == 'POST':
		date = form.date.data
		username = form.name.data
		report = form.report.data
		rate = form.rate.data
		if rate == 'bom':
			rate = 1
		elif rate == 'medio':
			rate = 2
		else:
			rate = 3
		if datetime.now().date()<date:
			flash('Data é inválida', 'warning')
			choices.clear()
			return redirect(url_for('professor_dash'))
		

		cur = mysql.connection.cursor()
		p = cur.execute("SELECT date FROM progress WHERE username = %s", [username])
		entered = []
		q = cur.fetchall()
		for i in range(p):
			entered.append(q[i]['date'])
		

		if date in entered:
			cur.execute("UPDATE progress SET daily_result = %s, rate = %s WHERE username = %s and date = %s", (report,rate, username, date))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('Atualizado com sucesso', 'success')
			return redirect(url_for('professor_dash'))
		

		cur.execute("INSERT INTO progress(username, date, daily_result, rate) VALUES(%s, %s, %s, %s)", (username, date, report, rate))
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Progresso atualizado e relatado', 'info')
		return redirect(url_for('professor_dash'))

	return render_template('professor_dash.html', livros = livros, form = form, alunos = alunos_under)
