from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from . import db
from .models import CentroTrabajo
from .security import roles_required,registrar_auditoria
from sqlalchemy.exc import IntegrityError
centros_bp=Blueprint('centros',__name__)
@centros_bp.route('/')
@login_required
@roles_required('admin','auditor')
def listar():
    page=request.args.get('page',1,type=int); centros=CentroTrabajo.query.order_by(CentroTrabajo.nombre).paginate(page=page,per_page=15,error_out=False); return render_template('centros/lista.html',centros=centros)
@centros_bp.route('/nuevo',methods=['GET','POST'])
@login_required
@roles_required('admin','auditor')
def nuevo():
    if request.method=='POST':
        try:
            n=CentroTrabajo(codigo=request.form['codigo'].strip().upper(),nombre=request.form['nombre'].strip()); db.session.add(n); db.session.commit(); registrar_auditoria('CREAR','CENTROS',n.nombre); return redirect(url_for('centros.listar'))
        except IntegrityError: db.session.rollback(); flash('Código o nombre ya existe.','danger')
    return render_template('centros/form.html',centro=None)
@centros_bp.route('/<int:id>/editar',methods=['GET','POST'])
@login_required
@roles_required('admin','auditor')
def editar(id):
    c=CentroTrabajo.query.get_or_404(id)
    if request.method=='POST': c.nombre=request.form['nombre'].strip(); c.activo=request.form.get('activo','1')=='1'; db.session.commit(); registrar_auditoria('EDITAR','CENTROS',c.nombre); return redirect(url_for('centros.listar'))
    return render_template('centros/form.html',centro=c)
@centros_bp.route('/<int:id>/eliminar',methods=['POST'])
@login_required
@roles_required('admin','auditor')
def eliminar(id):
    c=CentroTrabajo.query.get_or_404(id)
    if c.carpetas: flash('No se puede eliminar: tiene carpetas asociadas.','danger')
    else: db.session.delete(c); db.session.commit(); flash('Centro eliminado.','success')
    return redirect(url_for('centros.listar'))
