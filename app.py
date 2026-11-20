from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Clave para administrar las sesiones
app.secret_key = "clave_secreta_ods14_2026"

# Nombre de la base de datos
DATABASE = "usuarios.db"


# CONEXIÓN CON LA BASE DE DATOS
def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


# CREAR TABLA DE USUARIOS
def crear_tabla():
    conexion = conectar()
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()


# FUNCIÓN PARA GUARDAR USUARIOS (INSERT)
def guardar(usuario, password):
    conexion = conectar()
    password_encriptada = generate_password_hash(password)
    try:
        conexion.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
            (usuario, password_encriptada)
        )
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()


# FUNCIÓN PARA VALIDAR EL INICIO DE SESIÓN (SELECT)
def validar(usuario, password):
    conexion = conectar()
    usuario_encontrado = conexion.execute(
        "SELECT * FROM usuarios WHERE usuario = ?",
        (usuario,)
    ).fetchone()
    conexion.close()

    if usuario_encontrado:
        if check_password_hash(usuario_encontrado["password"], password):
            return usuario_encontrado
    return None


# PÁGINA PRINCIPAL: INICIO DE SESIÓN
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        password = request.form["password"]

        resultado = validar(usuario, password)
        if resultado:
            session["usuario"] = resultado["usuario"]
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")

    return render_template("index-sesion.html")


# REGISTRO DE USUARIOS
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        password = request.form["password"]
        confirmar = request.form["confirmar"]

        if not usuario or not password:
            flash("Completá todos los campos.", "error")
        elif len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
        elif password != confirmar:
            flash("Las contraseñas no coinciden.", "error")
        else:
            resultado = guardar(usuario, password)
            if resultado:
                flash("¡Cuenta creada correctamente! Ya podés iniciar sesión.", "exito")
                return redirect(url_for("login"))
            else:
                flash("Ese nombre de usuario ya está registrado.", "error")

    return render_template("registro.html")


# PÁGINA DESPUÉS DE INICIAR SESIÓN
@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "home-sesion.html",
        usuario=session["usuario"]
    )


# CERRAR SESIÓN
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# RUTAS OPCIONALES PARA TUS OTRAS PÁGINAS HTML (si las ponés en templates/)
@app.route("/index.html")
def pagina_inicio():
    return render_template("index.html")


@app.route("/efectos.html")
def pagina_efectos():
    return render_template("efectos.html")


@app.route("/reciclaje.html")
def pagina_reciclaje():
    return render_template("reciclaje.html")


@app.route("/creditos.html")
def pagina_creditos():
    return render_template("creditos.html")


# EJECUTAR APLICACIÓN
if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)