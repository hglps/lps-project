from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

def login_func(mysql):
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()

		result = cur.execute('SELECT * FROM info WHERE username = %s', [username])
		if result>0:
			data = cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate, password):
				session['logged_in'] = True
				session['username'] = username
				session['profile'] = data['profile']
				flash('Logado com sucesso', 'success')
				if session['profile'] == 1:
					return redirect(url_for('admin_dash'))
				if session['profile'] == 2:
					return redirect(url_for('secretaria_dash'))
				if session['profile'] == 3:
					return redirect(url_for('professor_dash'))
				return redirect(url_for('aluno_dash', username = username))
			else:
				error = 'Login: Invalido'
				return render_template('login.html', error = error)
			cur.close()
		else:
			error = 'Nome de Usuário não foi encontrado'
			return render_template('login.html', error = error)

	return render_template('login.html')