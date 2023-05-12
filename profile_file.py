from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

class ChangePasswordForm(Form):
	old_password = PasswordField('Senha atual')
	new_password = PasswordField('Nova senha', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'As senhas informadas não coincidem')
	])
	confirm = PasswordField('Confirmar senha')

class EditForm(Form):
    name = StringField('Nome', [validators.Length(min=1, max=50)])
    phone = StringField('Número de Telefone', [validators.Length(min = 1, max = 100)])

def update(username,mysql):
	form = ChangePasswordForm(request.form)
	if request.method == 'POST' and form.validate():
		new = form.new_password.data
		entered = form.old_password.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT password FROM info WHERE username = %s", [username])
		old = (cur.fetchone())['password']
		if sha256_crypt.verify(entered, old):
			cur.execute("UPDATE info SET password = %s WHERE username = %s", (sha256_crypt.encrypt(new), username))
			mysql.connection.commit()
			cur.close()
			flash('A nova senha funcionará no próximo Login', 'info')
			return redirect(url_for('aluno_dash', username = session['username']))
		cur.close()
		flash('A senha atual informada está incorreta', 'warning')
	return render_template('updatePassword.html', form = form)

def look_prof(username,mysql):
	if username == session['username'] or session['profile']==1 or session['profile']==2:
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM info WHERE username = %s", [username])
		result = cur.fetchone()
		return render_template('profile.html', result = result)
	flash('Você não pode ver o perfil de outra pessoa', 'warning')
	if session['profile']==3:
		return redirect(url_for('professor_dash'))
	return redirect(url_for('aluno_dash', username = username))

def edit_prof(username,mysql):
	if username != session['username']:
		flash('Você não está autorizado a editar os detalhes de outra pessoa', 'warning')
		if session['profile']==1:
			return redirect(url_for('admin_dash'))
		if session['profile']==2:
			return redirect(url_for('secretaria_dash', username = username))
		if session['profile']==3:
			return redirect(url_for('professor_dash', username = username))
		if session['profile']==4:
			return redirect(url_for('aluno_dash', username = username))

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM info WHERE username = %s", [username]);
	result = cur.fetchone()

	form = EditForm(request.form)
	
	form.name.data = result['name']
	form.phone.data = result['phone']

	cur.close()

	if request.method == 'POST' and form.validate():
		name = request.form['name']
		phone = request.form['phone']
		cur = mysql.connection.cursor()

		q = cur.execute("UPDATE info SET name = %s, phone = %s WHERE username = %s", (name, phone, username))
		mysql.connection.commit()
		cur.close()
		flash('Perfil atualizado com sucesso', 'success')
		if session['profile']==1:
			return redirect(url_for('admin_dash'))
		if session['profile']==2:
			return redirect(url_for('secretaria_dash', username = username))
		if session['profile']==3:
			return redirect(url_for('professor_dash', username = username))
		if session['profile']==4:
			return redirect(url_for('aluno_dash', username = username))
	return render_template('edit_profile.html', form=form)

