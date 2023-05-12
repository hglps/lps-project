from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt


choices = []
values = []
choices2 = []

class AddAlunoForm(Form):
    name = StringField('Nome', [validators.Length(min=1, max=50)])
    username = StringField('Nome de Usuário', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
    password = PasswordField('Senha', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='As senhas inseridas não sao iguais')
    ])
    confirm = PasswordField('Confirmar senha')
    plan  = RadioField('Selecionar um plano de estudo', choices = choices)
    professor = SelectField('Selecionar professor', choices = choices2)
    phone = StringField('Número de Telefones', [validators.Length(min = 1, max = 100)])


def add(mysql):
	cur = mysql.connection.cursor()
	
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	
	q = cur.execute("SELECT DISTINCT name FROM plans")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['name'],b[i]['name'])
		choices.append(tup)
	
	q = cur.execute("SELECT username FROM professors")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices2.append(tup)
	
	cur.close()
	
	form = AddAlunoForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		phone = form.phone.data
		plan = form.plan.data
		professor = form.professor.data
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, profile, phone) VALUES(%s, %s, %s, %s, %s)", (name, username, password, 4,phone))
		cur.execute("INSERT INTO alunos(username, plan, professor) VALUES(%s, %s, %s)", (username, plan, professor))
		mysql.connection.commit()
		cur.close()
		choices2.clear()
		choices.clear()
		flash('Novo aluno adicionado', 'success')
		if(session['profile']==1):
			return redirect(url_for('admin_dash'))
		return redirect(url_for('secretaria_dash'))
	return render_template('add_aluno.html', form=form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM alunos")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = delete.DeleteSecretariaForm(request.form)
	if request.method == 'POST':
		username = form.username.data
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM alunos WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Aluno deletado com sucesso', 'success')
		if(session['profile']==1):
			return redirect(url_for('admin_dash'))
		return redirect(url_for('secretaria_dash'))
	return render_template('delete_secretaria.html', form = form)

def openDash(username, mysql):
	if session['profile']==4 and username!=session['username']:
		flash('Usuário não autorizado a visualizar essa página', 'danger')
		return redirect(url_for('aluno_dash', username = session['username']))
	if session['profile']!=4:
		if session['profile']==1:
			return redirect(url_for('admin_dash'))
		if session['profile']==2:
			return redirect(url_for('secretaria_dash', username = username))
		if session['profile']==3:
			return redirect(url_for('professor_dash', username = username))	
	cur = mysql.connection.cursor()
	cur.execute("SELECT plan FROM alunos WHERE username = %s", [username])
	plan = (cur.fetchone())['plan']
	cur.execute("SELECT topics, name_livros FROM plans WHERE name = %s", [plan])
	scheme = cur.fetchall()
	n = cur.execute("SELECT date, daily_result, rate FROM progress WHERE username = %s ORDER BY date DESC", [username])
	progress = cur.fetchall()
	result = []
	for i in range(n):
		result.append(int(progress[i]['rate']))
	if len(result) != 0: 
		good = result.count(1)
		average = result.count(2)
		poor = result.count(3)
		total = good + poor + average
	else:
		good = 0
		poor = 0
		average = 0
		total = 1
	good = round((good/total) * 100, 2)
	average = round((average/total) * 100, 2)
	poor = round((poor/total) * 100, 2)
	cur.close()
	return render_template('aluno_dash.html',user = username, plan = plan, scheme = scheme, progress = progress, good = good, poor = poor, average = average)