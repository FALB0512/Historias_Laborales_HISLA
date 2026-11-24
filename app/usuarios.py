from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from flask_login import login_required,current_user
from . import db
from .models import Usuario
from .security import roles_required,registrar_auditoria
from sqlalchemy.exc import IntegrityError
usuarios_bp=Blueprint('usuarios',__name__)

def proteger_auditor(u):
    if u.rol=='auditor' and current_user.rol!='auditor': abort(403)

@usuarios_bp.route('/')
@login_required
@roles_required('admin','auditor')
def listar():
    page=request.args.get('page',1,type=int)
    usuarios=Usuario.query.order_by(Usuario.nombre).paginate(page=page,per_page=10,error_out=False)
    roles=['admin','asistente'] if current_user.rol=='admin' else ['admin','asistente','auditor']
    return render_template('usuarios/lista.html',usuarios=usuarios,roles=roles)

@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@roles_required("admin", "auditor")
def nuevo():
    roles = (
        ["admin", "asistente"]
        if current_user.rol == "admin"
        else ["admin", "asistente", "auditor"]
    )

    if request.method == "POST":
        try:
            nombre = request.form["nombre"].strip()
            username = request.form["username"].strip()
            email = request.form["email"].strip().lower()
            rol = request.form["rol"]
            password = request.form["password"]

            if rol not in roles:
                abort(403)

            usuario_existente = Usuario.query.filter(
                (Usuario.username == username) |
                (Usuario.email == email)
            ).first()

            if usuario_existente:
                if usuario_existente.username == username:
                    flash(
                        "El nombre de usuario ingresado ya existe. "
                        "Use otro nombre de usuario.",
                        "danger"
                    )
                elif usuario_existente.email == email:
                    flash(
                        "El correo ingresado ya está registrado. "
                        "Use otro correo o edite el usuario existente.",
                        "danger"
                    )

                return redirect(url_for("usuarios.nuevo"))

            nuevo_usuario = Usuario(
                nombre=nombre,
                username=username,
                email=email,
                rol=rol,
                debe_cambiar_password=True,
                activo=True
            )

            nuevo_usuario.set_password(password)

            db.session.add(nuevo_usuario)
            db.session.commit()

            registrar_auditoria(
                "CREAR",
                "USUARIOS",
                f"Usuario {nuevo_usuario.username}, rol {nuevo_usuario.rol}"
            )

            flash("Usuario creado correctamente.", "success")

            return redirect(url_for("usuarios.listar"))

        except IntegrityError:
            db.session.rollback()

            flash(
                "No fue posible crear el usuario porque el correo o el nombre "
                "de usuario ya se encuentra registrado.",
                "danger"
            )

            return redirect(url_for("usuarios.nuevo"))

        except Exception as e:
            db.session.rollback()

            flash(
                f"No fue posible crear el usuario. Detalle: {str(e)}",
                "danger"
            )

            return redirect(url_for("usuarios.nuevo"))

    return render_template(
        "usuarios/form.html",
        roles=roles,
        usuario=None
    )

@usuarios_bp.route('/<int:id>/editar',methods=['GET','POST'])
@login_required
@roles_required('admin','auditor')
def editar(id):
    u=Usuario.query.get_or_404(id); proteger_auditor(u)
    roles=['admin','asistente'] if current_user.rol=='admin' else ['admin','asistente','auditor']
    if request.method=='POST':
        if request.form['rol'] not in roles: abort(403)
        u.nombre=request.form['nombre']; u.email=request.form['email']; u.rol=request.form['rol']; db.session.commit(); registrar_auditoria('EDITAR','USUARIOS',u.username)
        return redirect(url_for('usuarios.listar'))
    return render_template('usuarios/form.html',roles=roles,usuario=u)

@usuarios_bp.route('/<int:id>/toggle',methods=['POST'])
@login_required
@roles_required('admin','auditor')
def toggle(id):
    u=Usuario.query.get_or_404(id); proteger_auditor(u)
    if u.id==current_user.id: flash('No puede desactivar su propio usuario.','danger')
    else: u.activo=not u.activo; db.session.commit(); registrar_auditoria('ACTIVAR_DESACTIVAR','USUARIOS',u.username)
    return redirect(url_for('usuarios.listar'))

@usuarios_bp.route('/<int:id>/eliminar',methods=['POST'])
@login_required
@roles_required('admin','auditor')
def eliminar(id):
    u=Usuario.query.get_or_404(id); proteger_auditor(u)
    if u.id==current_user.id: abort(400)
    name=u.username; db.session.delete(u); db.session.commit(); registrar_auditoria('ELIMINAR','USUARIOS',name)
    return redirect(url_for('usuarios.listar'))
