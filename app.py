from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "123456"

# -------------------------
# CREAR BASE DE DATOS
# -------------------------

def crear_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        nombre TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO usuarios
    (id, username, password, nombre)
    VALUES
    (1,'admin','123456','Administrador')
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO productos
    (id,codigo,nombre,descripcion,precio,stock,categoria)
    VALUES
    (1,'P001','Laptop Lenovo','Core i5',2500,15,'Computo')
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO productos
    (id,codigo,nombre,descripcion,precio,stock,categoria)
    VALUES
    (2,'P002','Mouse Logitech','Inalambrico',80,50,'Accesorios')
    """)

    conn.commit()
    conn.close()

crear_db()

# -------------------------
# LOGIN
# -------------------------

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT nombre
        FROM usuarios
        WHERE username=? AND password=?
        """, (usuario, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["usuario"] = user[0]

            return redirect("/principal")

    return render_template("login.html")

# -------------------------
# PRINCIPAL
# -------------------------

@app.route("/principal")
def principal():

    if "usuario" not in session:
        return redirect("/login")

    return render_template(
        "principal.html",
        nombre=session["usuario"]
    )

# -------------------------
# BUSCADOR
# -------------------------

@app.route("/buscador")
def buscador():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("buscador.html")

# -------------------------
# API BUSCAR PRODUCTO
# -------------------------

@app.route("/api/buscar_producto", methods=["POST"])
def buscar_producto():

    codigo = request.form["codigo"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT codigo,nombre,descripcion,precio,stock,categoria
    FROM productos
    WHERE codigo=?
    """, (codigo,))

    producto = cursor.fetchone()

    conn.close()

    if producto:

        return jsonify({
            "codigo": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio": producto[3],
            "stock": producto[4],
            "categoria": producto[5]
        })

    return jsonify({
        "mensaje": "Producto no encontrado"
    })

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# -------------------------

if __name__ == "__main__":
    app.run(debug=True)