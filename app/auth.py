from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Usuario
from .security import registrar_auditoria

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = Usuario.query.filter_by(username=request.form["username"].strip()).first()
        if not usuario or not usuario.check_password(request.form["password"]):
            flash("Credenciales inválidas.", "danger")
            return render_template("auth/login.html")
        if not usuario.activo:
            flash("El usuario está desactivado.", "danger")
            return render_template("auth/login.html")
        login_user(usuario)
        registrar_auditoria("LOGIN", "SEGURIDAD", "Inicio de sesión")
        if usuario.debe_cambiar_password:
            return redirect(url_for("auth.cambiar_password"))
        return redirect(url_for("main.dashboard"))
    return render_template("auth/login.html")

@auth_bp.route("/cambiar-password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    if request.method == "POST":
        nueva = request.form["password"]
        confirmar = request.form["confirmar"]
        if len(nueva) < 8 or nueva != confirmar:
            flash("La contraseña debe tener mínimo 8 caracteres y coincidir.", "danger")
        else:
            current_user.set_password(nueva)
            current_user.debe_cambiar_password = False
            db.session.commit()
            registrar_auditoria("CAMBIO_PASSWORD", "SEGURIDAD")
            flash("Contraseña actualizada.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("auth/cambiar_password.html")

@auth_bp.route("/logout")
@login_required
def logout():
    registrar_auditoria("LOGOUT", "SEGURIDAD", "Cierre de sesión")
    logout_user()
    return redirect(url_for("auth.login"))
