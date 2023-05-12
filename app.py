from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_script import Manager
from functools import wraps
import profile_file
import login_file
import professor
import livro
import alunos
import plans
import secretaria

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'study_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.secret_key = 'secret_key_1_2_3'

mysql = MySQL(app)

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("Por favor, faça o Login", "danger")
			return redirect(url_for('login'))
	return wrap

def is_professor(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 3:
			return f(*args, **kwargs)
		else:
			flash('Usuário não é um professor', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 1:
			return f(*args, **kwargs)
		else:
			flash('Usuário não é um Admin', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_secretaria_level(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] <= 2:
			return f(*args, **kwargs)
		else:
			flash('Usuário não tem autorização para visualizar esta página', 'danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	result = login_file.login_func(mysql)
	return result


@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
def update_password(username):
	result = profile_file.update(username,mysql)
	return result

@app.route('/admin_dash')
@is_logged_in
@is_admin
def admin_dash():
	return render_template('admin_dash.html')

@app.route('/add_professor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def add_professor():
	result = professor.add(mysql)
	return result

@app.route('/delete_professor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def delete_professor():
	result = professor.delete(mysql)
	return result

@app.route('/add_secretaria', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def add_secretaria():
	result = secretaria.add(mysql)
	return result

@app.route('/delete_secretaria', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def delete_secretaria():
	result = secretaria.delete(mysql)
	return result

@app.route('/add_livro', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def add_livro():
	result = livro.add(mysql)
	return result

@app.route('/remove_livro', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def remove_livro():
	result = livro.delete(mysql)
	return result

@app.route('/add_aluno', methods = ['GET', 'POST'])
@is_logged_in
@is_secretaria_level
def add_aluno():
	result = alunos.add(mysql)
	return result

@app.route('/delete_aluno', methods = ['GET', 'POST'])
@is_logged_in
@is_secretaria_level
def delete_aluno():
	result = alunos.delete(mysql)
	return result

@app.route('/viewDetails')
def viewDetails():
	cur = mysql.connection.cursor()
	cur.execute("SELECT username FROM info WHERE username != %s", [session['username']])
	result = cur.fetchall()
	return render_template('viewDetails.html', result = result)

@app.route('/secretaria_dash')
@is_secretaria_level
def secretaria_dash():
	return render_template('secretaria_dash.html')

@app.route('/professor_dash', methods = ['GET', 'POST'])
@is_logged_in
@is_professor
def professor_dash():
	result = professor.openDash(mysql)
	return result

@app.route('/updatePlans', methods = ['GET', 'POST'])
@is_professor
def updatePlans():
	result = plans.update(mysql)
	return result


@app.route('/aluno_dash/<string:username>')
@is_logged_in
def aluno_dash(username):
	result = alunos.openDash(username, mysql)
	return result

@app.route('/profile/<string:username>')
@is_logged_in
def profile(username):
	result = profile_file.look_prof(username,mysql)
	return result

@app.route('/edit_profile/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def edit_profile(username):
	result = profile_file.edit_prof(username,mysql)
	return result

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('Logout com sucesso', 'success')
	return redirect(url_for('login'))


if __name__ == "__main__":
	app.debug = True
	manager = Manager(app)
	manager.run()