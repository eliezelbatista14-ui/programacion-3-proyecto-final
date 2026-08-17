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
    conexion.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        vestido_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (vestido_id) REFERENCES vestidos(id)
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

@app.route("/reservas", methods=["GET", "POST"])
def reservas():

    conexion = conectar_db()

    if request.method == "POST":

        cliente_id = request.form["cliente_id"]
        vestido_id = request.form["vestido_id"]
        fecha = request.form["fecha"]

        conexion.execute(
            """
            INSERT INTO reservas
            (cliente_id, vestido_id, fecha)
            VALUES (?, ?, ?)
            """,
            (cliente_id, vestido_id, fecha)
        )

        conexion.commit()

    clientes = conexion.execute(
        "SELECT * FROM clientes"
    ).fetchall()

    vestidos = conexion.execute(
        "SELECT * FROM vestidos WHERE estado = 'Disponible'"
    ).fetchall()

    reservas = conexion.execute("""
        SELECT
            reservas.id,
            clientes.nombre,
            vestidos.nombre,
            reservas.fecha
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN vestidos ON reservas.vestido_id = vestidos.id
    """).fetchall()

    conexion.close()

    return render_template(
        "reservas.html",
        clientes=clientes,
        vestidos=vestidos,
        reservas=reservas
    )
@app.route("/reservas/editar/<int:id>", methods=["GET", "POST"])
def editar_reserva(id):

    conexion = conectar_db()

    if request.method == "POST":

        cliente_id = request.form["cliente_id"]
        vestido_id = request.form["vestido_id"]
        fecha = request.form["fecha"]

        conexion.execute(
            """
            UPDATE reservas
            SET cliente_id = ?, vestido_id = ?, fecha = ?
            WHERE id = ?
            """,
            (cliente_id, vestido_id, fecha, id)
        )

        conexion.commit()
        conexion.close()

        return redirect("/reservas")

    reserva = conexion.execute(
        """
        SELECT * FROM reservas
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    clientes = conexion.execute(
        "SELECT * FROM clientes"
    ).fetchall()

    vestidos = conexion.execute(
        "SELECT * FROM vestidos"
    ).fetchall()

    conexion.close()

    return render_template(
        "editar_reserva.html",
        reserva=reserva,
        clientes=clientes,
        vestidos=vestidos
    )

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)
if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)