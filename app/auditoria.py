from flask import Blueprint,render_template,request
from flask_login import login_required
from .models import Auditoria
from .security import roles_required
auditoria_bp=Blueprint('auditoria',__name__)
@auditoria_bp.route('/')
@login_required
@roles_required('auditor')
def listar():
    page=request.args.get('page',1,type=int)
    registros=Auditoria.query.order_by(Auditoria.fecha.desc()).paginate(page=page,per_page=20,error_out=False)
    return render_template('auditoria/lista.html',registros=registros)
