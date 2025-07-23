
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Flask, render_template, request, redirect, url_for, session, flash 
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Guardar keys del archivo ambiente(env)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY") 

#Metodo Supabase (Conectarse con la base de datos)

supabase: Client = create_client(url, key)


@app.route('/')
def index():
    try:
        response = supabase.table('productos').select('*').execute() 
        productos = response.data
        return render_template('index.html', articulos = productos)
    except Exception as e:
        flash(f'Error al cargar articulos:{e}', 'danger')
        return render_template('index.html', articulos = [])

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        try: 
            user = supabase.auth.sign_up({'email': email, 'password' :password})
            print (user)
            flash('Registro Exitoso', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error al Registrarse:{e}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')    

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user= supabase.auth.sign_in_with_password({'email': email, 'password' :password})
            session['user'] = user.user.id
            session['user_email'] = user.user.email
            flash('Inicio de Sesion Exitoso', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al Inciar Sesion:{e}', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/catalogo')
def catalogo():
    return render_template("catalogo.html")
@app.route('/logout')
def logout():
    return render_template("index.html")








