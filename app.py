
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
        nombre_completo = request.form['nombre']
        try: 
            user = supabase.auth.sign_up({'email': email, 'password' :password})
            supabase.table('user_data').insert({
                'nombre_completo': nombre_completo,
                'rol_id':2,
                'user_id':user.user.id
            }).execute()
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
            data = supabase.table('user_data').select('*').eq('user_id', user.user.id).execute()
            print(data.data[0]['id'])
            session['user'] = user.user.id
            session['user_email'] = user.user.email
            session['user_nombre'] = data.data[0]['nombre_completo']
            session['user_rol'] = data.data[0]['rol_id']
            print(session)
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al Inciar Sesion:{e}', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/catalogo')
def catalogo():
    if 'user' not in session:
        return redirect (url_for('login'))
    
    usuario_id = session['user']
    print(usuario_id) 
    try:
        response = supabase.table('productos').select('*').eq('usuario_id', usuario_id).execute() 
        articulos = response.data
        print(articulos)
        return render_template('catalogo.html',  articulos = articulos)

    except Exception as e:
        flash(f'Error al cargar articulos:{e}', 'danger')
        return render_template('catalogo.html', articulos = [])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_email', None)
    flash("Sesion Cerrada", "info")
    return redirect (url_for('index'))

@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    if 'user' not in session:
        return redirect (url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        precio = request.form['precio']
        categoria = request.form['categoria']
        usuario_id = session['user']

        # Validaciones
        if not nombre or not descripcion or not precio or not stock or not categoria or not usuario_id:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('create_article'))

        try:
            # Insertar el artículo en la base de datos
            supabase.table('productos').insert({
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'stock': stock,
                'categoria': categoria,
                'usuario_id': usuario_id,
            }).execute()
            flash('Artículo creado exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al crear el artículo: {e}', 'danger')
            return redirect(url_for('create_article'))

    return render_template('formulario.html')

@app.route('/delete_article/<int:id>', methods=['POST'])
def delete_article(id):
    if 'user' not in session:
        return redirect (url_for('login'))

    usuario_id = session['user'] 
    try:
        supabase.table('productos').delete().eq('id', id).eq('usuario_id', usuario_id).execute()
        flash("Articulo Eliminado Correctamente", 'succes')
    except Exception as e:
        flash(f'Error al Eliminar Articulo:{e}', 'danger')
        print(e)
    return redirect(url_for('catalogo'))
    
@app.route('/carrito')
def carrito():
    return render_template("carrito.html") 
    

@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
def edit_article(id):
    #Validacion de Session
    if 'user' not in session:
        return redirect(url_for('login'))

    usuario_id = session['user']
    
    # Obtener el artículo existente
    response = supabase.table('productos').select('*').eq('id', id).eq('usuario_id', usuario_id).execute()
    articulo = response.data

    #Validacuion de Articulo
    if not articulo:
        flash('Artículo no encontrado', 'danger')
        return redirect(url_for('catalogo'))

    articulo = articulo[0]  # Obtener el primer (y único) artículo

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        precio = request.form['precio']
        categoria = request.form['categoria']

        # Validaciones de los datos
        if not nombre or not descripcion or not precio or not stock or not categoria:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('edit_article', id=id))

        try:
            # Actualizar el artículo en la base de datos
            supabase.table('productos').update({
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'stock': stock,
                'categoria': categoria,
            }).eq('id', id).eq('usuario_id', usuario_id).execute()
            flash('Artículo actualizado exitosamente', 'success')
            return redirect(url_for('catalogo'))
        except Exception as e:
            flash(f'Error al actualizar el artículo: {e}', 'danger')
            return redirect(url_for('edit_article', id=id))

    return render_template('formulario.html', articulo=articulo)

@app.route('/agregar_carrito/<int:id>', method=['GET', 'POST'])
def agregar_carrito(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        producto_id = request.form['producto_id']
        user_id = request.form['user_id']
        cantidad = request.form['cantidad']

    if not producto_id or not user_id or not cantidad :
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('create_article'))

    try:
            # Insertar el artículo en la base de datos
            supabase.table('Carrito').insert({
                'producto_id': producto_id,
                'user_id': user_id,
                'cantidad': cantidad,
            }).execute()
            flash('Agrgado al Carrito exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al agregar al carrito: {e}', 'danger')
            return redirect(url_for('index'))

    return render_template('formulario.html')

        
@app.route('/delete_carrito/<int:id>', methods=['POST'])
def delete_carrito(id):
    if 'user' not in session:
        return redirect (url_for('login'))

    usuario_id = session['user'] 
    try:
        supabase.table('Carrito').delete().eq('id', id).eq('user_id', usuario_id).execute()
        flash("Articulo Eliminado Correctamente", 'succes')
    except Exception as e:
        flash(f'Error al Eliminar Articulo:{e}', 'danger')
        print(e)
    return redirect(url_for('carrito'))








