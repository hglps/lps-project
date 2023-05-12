from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging

class UpdatePlanForm(Form):
    name = StringField('Nome do plano', [validators.Length(min=1, max=50)])
    topics = StringField('Topicos', [validators.Length(min = 1, max = 100)])
    name_livros = StringField('Nomes dos livros', [validators.Length(min = 1, max = 100)])

def update(mysql):
	form = UpdatePlanForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		topics = form.topics.data
		name_livros = form.name_livros.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT name, topics FROM plans WHERE name = %s and topics = %s", (name, topics))
		result = cur.fetchall()
		if len(result)>0:
			cur.execute("UPDATE plans SET name_livros = %s WHERE name = %s and topics = %s", (name_livros, name, topics))
		else:
			cur.execute("INSERT INTO plans(name, topics, name_livros) VALUES(%s, %s, %s)", (name, topics, name_livros))
		mysql.connection.commit()
		cur.close()
		flash('Plano de estudo atualizado com sucesso', 'success')
		return redirect(url_for('professor_dash'))
	return render_template('addPlan.html', form = form)
