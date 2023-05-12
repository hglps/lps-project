from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session

choices = []

class AddLivroForm(Form):
	name = StringField('Nome do livro', [validators.Length(min = 1, max = 100)])
	count = IntegerField('Quantidade', [validators.NumberRange(min = 1, max = 25)])

class RemoveLivroForm(Form):
	name = RadioField('Nome do livro', choices = choices)
	count = IntegerField('Quantidade', [validators.InputRequired()])

def add(mysql):
	form = AddLivroForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		count = form.count.data
		cur = mysql.connection.cursor()
		q = cur.execute("SELECT name FROM livros")
		livros = []
		b = cur.fetchall()
		for i in range(q):
			livros.append(b[i]['name'])
		if name in livros:
			cur.execute("UPDATE livros SET count = count+%s WHERE name = %s", (count, name))
		else:
			cur.execute("INSERT INTO livros(name, count) VALUES(%s, %s)", (name, count))
		mysql.connection.commit()
		cur.close()
		flash('Novo livro adicionado', 'success')
		return redirect(url_for('admin_dash'))
	return render_template('add_livro.html', form = form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT name FROM livros")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['name'],b[i]['name'])
		choices.append(tup)
	form = RemoveLivroForm(request.form)
	if request.method == 'POST' and form.validate():
		cur.execute("SELECT * FROM livros WHERE name = %s", [form.name.data])
		data = cur.fetchone()
		num = data['count']
		if num >= form.count.data and form.count.data>0:
			name = form.name.data
			count = form.count.data
			cur = mysql.connection.cursor()
			cur.execute("UPDATE livros SET count = count-%s WHERE name = %s", (count, name))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('Livro removido com sucesso', 'success')
			return redirect(url_for('admin_dash'))
		else:
			flash('Deve inserir um número válido', 'danger')
	return render_template('remove_livro.html', form = form)
