from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def conectar_db():
    return sqlite3.connect(DATABASE)


def crear_tabla():
    conexion = conectar_db()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT
        )
    """)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS vestidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


@app.route("/")
def inicio():

    busqueda = request.args.get("busqueda", "")

    conexion = conectar_db()

    if busqueda:
        clientes = conexion.execute(
            """
            SELECT * FROM clientes
            WHERE nombre LIKE ? OR telefono LIKE ?
            """,
            (f"%{busqueda}%", f"%{busqueda}%")
        ).fetchall()
    else:
        clientes = conexion.execute(
            "SELECT * FROM clientes"
        ).fetchall()

    conexion.close()

    return render_template(
        "clientes.html",
        clientes=clientes,
        busqueda=busqueda
    )

@app.route("/clientes", methods=["POST"])
def registrar_cliente():

    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    conexion = conectar_db()

    conexion.execute(
        """
        INSERT INTO clientes (nombre, telefono, correo)
        VALUES (?, ?, ?)
        """,
        (nombre, telefono, correo)
    )

    conexion.commit()
    conexion.close()

    return redirect("/")

@app.route("/vestidos", methods=["GET", "POST"])
def vestidos():

    conexion = conectar_db()

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        estado = request.form["estado"]

        conexion.execute(
            """
            INSERT INTO vestidos
            (nombre, descripcion, precio, estado)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, descripcion, precio, estado)
        )

        conexion.commit()

    vestidos = conexion.execute(
        "SELECT * FROM vestidos"
    ).fetchall()

    conexion.close()

    return render_template(
        "vestidos.html",
        vestidos=vestidos
    )

@app.route("/disponibilidad")
def disponibilidad():

    estado = request.args.get("estado", "")

    conexion = conectar_db()

    if estado:
        vestidos = conexion.execute(
            """
            SELECT * FROM vestidos
            WHERE estado = ?
            """,
            (estado,)
        ).fetchall()
    else:
        vestidos = conexion.execute(
            "SELECT * FROM vestidos"
        ).fetchall()

    conexion.close()

    return render_template(
        "disponibilidad.html",
        vestidos=vestidos,
        estado=estado
    )

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)