from flask import flask, render_template, render_template, redirect, flash
import sqlite3

app = flask(__name__)
app.secrete_key = "minha_chave_secreta"

def criar_banco():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TEBLE IF NOT EXISTS
    usuarios(
            id INTEGER PRYMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL  )
                """)
    conn.commit()
    conn.close()
criar_banco()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/cadastro")
def cadastro():
    return
render_template("cadastro.html")
@app.route("/registar" , methods=["post"])
def registar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]

    conn = sqlite3.connect("datanbase.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuarios(nome, email, senha) VALUES (?,?,?)",
        (nome, email, senha))
            conn.commit()
            flash("cadastro realizado com sucesso!","success")
            return redirect("/")
        except:
            flash("email ja cadastrado!", "error")
            return redirect("/cadastro")
        finally:
            conn.close()
@app.route("/autenticar",
methods=["post"])
def autenticar():
    email = request.form["email"]
    senha = request.form["senha"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email,senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        return "login ok usuario autenticado!"
    else:
        return"Email ou senha incoretos!"
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
