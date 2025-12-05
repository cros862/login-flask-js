import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave_secreta_123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")


# ========================= BANCO =========================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

init_db()


def get_user(email, senha):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, ativo FROM usuarios WHERE email=? AND senha=?", (email, senha))
    user = cur.fetchone()
    conn.close()
    return user


# ========================= ROTAS =========================

@app.route("/")
def index():
    return redirect(url_for("login"))


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = get_user(email, senha)

        if not user:
            erro = "E-mail ou senha incorretos."
        else:
            if user[3] == 0:
                erro = "Este usuário está inativo."
            else:
                session["user_id"] = user[0]
                session["user_name"] = user[1] if user[1] else email
                session["user_email"] = user[2]

                return redirect(url_for("home"))

    return render_template("login.html", erro=erro)


# ---------- CADASTRO ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    erro = None

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                        (nome, email, senha))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            erro = "E-mail já registrado."

    return render_template("register.html", erro=erro)


# ---------- HOME ----------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("home.html", usuario=session["user_name"])


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===========================================================
#                   ÁREA ADMINISTRATIVA
# ===========================================================

ADMIN_EMAIL = "admin@admin.com"   # <= só ele pode acessar


@app.route("/admin")
def admin():
    # VERIFICA se está logado
    if "user_email" not in session:
        return redirect(url_for("login"))

    # VERIFICA se é o administrador
    if session["user_email"] != ADMIN_EMAIL:
        return "<h1>ENTRADA NEGADA ❌</h1> <p>Apenas o administrador pode acessar esta página.</p>"

    # CARREGAR USUÁRIOS
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, ativo FROM usuarios")
    usuarios = cur.fetchall()
    conn.close()

    return render_template("admin.html", usuarios=usuarios)


# ATIVAR / INATIVAR
@app.route("/toggle/<int:user_id>")
def toggle_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET ativo = 1 - ativo WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# APAGAR USUÁRIO
@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# ========================= RUN =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
