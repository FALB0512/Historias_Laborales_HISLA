from functools import wraps
from flask import abort, request
from flask_login import current_user
from . import db
from .models import Auditoria

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.activo:
                abort(403)
            if current_user.rol not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def registrar_auditoria(accion, modulo, detalle=""):
    registro = Auditoria(
        usuario_id=current_user.id if current_user.is_authenticated else None,
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr)
    )
    db.session.add(registro)
    db.session.commit()
