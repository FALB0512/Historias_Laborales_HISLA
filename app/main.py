from datetime import date
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from .models import Persona, CarpetaFisica, CentroTrabajo, ConsecutivoCarpeta, Prestamo
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def dashboard():
    total_personas = Persona.query.count()
    total_carpetas = CarpetaFisica.query.count()
    personas_multiples = db_count = (Persona.query.join(CarpetaFisica).group_by(Persona.id).having(func.count(CarpetaFisica.id) > 1).count())
    activas = CarpetaFisica.query.filter_by(estado="activo", archivada=False).count()
    retiradas = CarpetaFisica.query.filter_by(estado="retirado", archivada=False).count()
    prestamos_activos = Prestamo.query.filter_by(estado="prestado").count()
    prestamos_vencidos = Prestamo.query.filter(Prestamo.estado=="prestado", Prestamo.fecha_devolucion_prevista < date.today()).count()
    por_centro = (CarpetaFisica.query.with_entities(CentroTrabajo.nombre, func.count(CarpetaFisica.id).label("cantidad"))
        .join(CentroTrabajo).group_by(CentroTrabajo.id, CentroTrabajo.nombre)
        .order_by(func.count(CarpetaFisica.id).desc()).limit(8).all())
    ultimos_prestamos = Prestamo.query.order_by(Prestamo.fecha_prestamo.desc()).limit(5).all()
    return render_template("dashboard.html", total_personas=total_personas, total_carpetas=total_carpetas,
        personas_multiples=personas_multiples, activos=activas, retirados=retiradas,
        prestamos_activos=prestamos_activos, prestamos_vencidos=prestamos_vencidos,
        por_centro=por_centro, ultimos_prestamos=ultimos_prestamos)
