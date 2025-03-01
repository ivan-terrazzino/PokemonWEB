# Pokemon Api

Esta WEB proporciona acceso a diferentes funcionalidades relacionadas con Pokémon, permitiendo a los usuarios interactuar con ella para buscar nombres y tipos de pokemones.

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [Dependencias](#dependencias)
3. [Autenticación](#Autenticación)
4. [Uso](#uso)


## Instalación

Para instalar sus dependencias, sigue estos pasos:

1. Instalar las dependencias del archivo "requirements.txt".
pip install -r requirements.txt

## Dependencias

Este proyecto depende de las siguientes bibliotecas:

Flask: Para crear una aplicación web ligera.
requests: Para hacer peticiones HTTP.
random: Para generar los jwt y realizar validaciones de credenciales.

## Autenticación
La API utiliza autenticación mediante tokens JWT para asegurar que solo los usuarios autenticados puedan realizar estas operaciones.

## Uso

1. Generar las variables de entorno con las credenciales, ya que de esta forma podremos autenticarnos en la API.
export SECRET_KEY="tu_clave_secreta"
export POKEMON_USER="mi_usuario"
export POKEMON_PASS="mi_contraseña"

2. Iniciar la API (La misma se inicia en http://localhost:5000)
python main.py