from flask import Flask, request, render_template, redirect, make_response, url_for
import random
import string
import os
import requests
import jwt
import datetime

# Función para generar un token de sesión JWT
def generar_token(username):
    secret_key = os.getenv('SECRET_KEY')
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # El token expira en 10 minutos
    payload = {
        'username': username,
        'exp': expiration_time
    }
    
    # Generar el JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

# Función auxiliar para obtener información del Pokémon desde la API
def obtener_info_pokemon(pokemon_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

# Crear una nueva aplicación Flask
app = Flask(__name__)

# Ruta de inicio
@app.route('/')
def index():
    return render_template('login.html')

# Ruta para manejar el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    pokemon_user = os.getenv('POKEMON_USER')
    pokemon_pass = os.getenv('POKEMON_PASS')

    if username == pokemon_user and password == pokemon_pass:
        # Generar el token JWT
        token = generar_token(username)

        # Crear la respuesta y establecer la cookie
        response = make_response(render_template('menu.html', token=token))
        
        # Establecer el token en la cookie con la opción 'HttpOnly' para mayor seguridad
        response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict', max_age=datetime.timedelta(hours=1))

        return response
    else:
        return render_template('login.html', error_message="Usuario o contraseña incorrectos.")

# Función para verificar el token JWT desde las cookies
def verificar_token():
    token = request.cookies.get('auth_token')  # Obtener el token de las cookies
    if token is None:
        return None

    try:
        secret_key = os.getenv('SECRET_KEY', 'mi_clave_secreta')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # El token ha expirado
    except jwt.InvalidTokenError:
        return None  # El token es inválido

# Ruta del menú
@app.route('/menu')
def menu():
    # Verificar si el token está presente y es válido
    if verificar_token() is None:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado

    return render_template('menu.html')

# Ruta para la búsqueda de Pokémon
@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():
    # Verificar si el token está presente y es válido
    if verificar_token() is None:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado

    pokemon_name = request.form.get('pokemon_name')

    if not pokemon_name:
        return render_template('busqueda.html', error_message="No se ha indicado el nombre de un Pokémon.")

    pokemon_info = obtener_info_pokemon(pokemon_name)
    if not pokemon_info:
        return render_template('busqueda.html', error_message="No se pudo encontrar el Pokémon.")

    info = [pokemon_info['name'], pokemon_info['types'][0]['type']['name'], pokemon_info['id']]
    return render_template('mostrarpokemon.html', info=info)

# Ruta para la ruleta de Pokémon
@app.route('/ruleta', methods=['POST', 'GET'])
def ruleta():
    # Verificar si el token está presente y es válido
    if verificar_token() is None:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado

    if request.method == 'POST':
        tipo_pokemon = request.form.get('tipo_pokemon')
        url = f'https://pokeapi.co/api/v2/type/{tipo_pokemon}'
        response = requests.get(url)

        if response.status_code != 200:
            return render_template('ruleta.html', error_message="No se pudo obtener la información de los Pokémon.")

        json_data = response.json()
        pokemon_names = [item['pokemon']['name'] for item in json_data['pokemon']]
        pokemon_name = random.choice(pokemon_names)

        pokemon_info = obtener_info_pokemon(pokemon_name)
        if not pokemon_info:
            return render_template('busqueda.html', error_message="No se pudo encontrar el Pokémon.")

        tipos_str = ' / '.join([item['type']['name'] for item in pokemon_info['types']])
        info = [pokemon_info['name'], tipos_str, pokemon_info['id']]
        return render_template('mostrarpokemon.html', info=info)
    
    return render_template('ruleta.html')

@app.route('/nombre-mas-largo', methods=['POST', 'GET'])
def nombremaslargo():
    # Verificar si el token está presente y es válido
    if verificar_token() is None:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado

    if request.method == 'POST':
        tipo_pokemon = request.form.get('tipo_pokemon')
        
        # Verificar si el tipo de Pokémon fue proporcionado
        if not tipo_pokemon:
            return render_template('nombremaslargo.html', error_message="¡Debes ingresar un tipo de Pokémon!")

        # Si se proporciona un tipo, construir la URL para obtener los Pokémon de ese tipo
        url = f'https://pokeapi.co/api/v2/type/{tipo_pokemon}'
        
        response = requests.get(url)

        if response.status_code != 200:
            return render_template('nombremaslargo.html', error_message="No se pudo obtener la información de los Pokémon.")

        json_data = response.json()
        
        # Extraer los nombres de los Pokémon del tipo proporcionado
        pokemon_names = [item['pokemon']['name'] for item in json_data['pokemon']]

        # Obtener el nombre más largo
        pokemon_name = max(pokemon_names, key=len)

        # Obtener la información del Pokémon con el nombre más largo
        pokemon_info = obtener_info_pokemon(pokemon_name)
        if not pokemon_info:
            return render_template('nombremaslargo.html', error_message="No se pudo encontrar el Pokémon.")

        # Crear un string con todos los tipos del Pokémon
        tipos_str = ' / '.join([item['type']['name'] for item in pokemon_info['types']])

        # Información que se mostrará
        info = [pokemon_info['name'], tipos_str, pokemon_info['id']]
        
        return render_template('mostrarpokemon.html', info=info)

    return render_template('nombremaslargo.html')



@app.route('/logout', methods=['POST'])
def logout():
    # Crear una respuesta para cerrar sesión
    response = make_response(redirect(url_for('index')))  # Redirigir a la página de inicio (login)
    
    # Eliminar la cookie del token JWT
    response.delete_cookie('auth_token')  # Borra la cookie 'auth_token'
    
    return response

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=5000)


