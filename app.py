import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "troque_por_uma_chave_secreta_mais_forte"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

#
def get_user_by_email_and_pass(email, senha):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios WHERE email=? AND senha=?", (email, senha))
    u = cur.fetchone()
    conn.close()
    return u

@app.route("/", methods=["GET"])
def root():
    # manda para login (mais claro)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        user = get_user_by_email_and_pass(email, senha)
        if user:
            # user -> (id, nome, email)
            session["user_id"] = user[0]
            session["user_name"] = user[1] if user[1] else user[2]
            return redirect(url_for("home"))
        else:
            erro = "Email ou senha incorretos."
    return render_template("login.html", erro=erro)

@app.route("/register", methods=["GET", "POST"])
def register():
    erro = None
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not email or not senha:
            erro = "Email e senha são obrigatórios."
            return render_template("register.html", erro=erro)

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                        (nome, email, senha))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            erro = "Esse e-mail já está cadastrado."
        except Exception as e:
            erro = "Erro ao criar conta: " + str(e)
    return render_template("register.html", erro=erro)

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    usuario = session.get("user_name", "Usuário")
    return render_template("home.html", usuario=usuario)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Modo dev com reload e host aberto (Codespaces)
    app.run(host="0.0.0.0", port=5000, debug=True)
