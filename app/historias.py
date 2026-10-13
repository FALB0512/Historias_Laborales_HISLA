from datetime import datetime, date
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from . import db
from .models import Persona, CarpetaFisica, TipoDocumento, UnidadConservacion, CentroTrabajo, ConsecutivoCarpeta
from .security import roles_required, registrar_auditoria
historias_bp = Blueprint("historias", __name__)

def _clean(v): return " ".join((v or "").replace("\xa0"," ").strip().split())

def _parse_date(v):
    try: return datetime.strptime(v, "%Y-%m-%d").date()
    except Exception: return None

@historias_bp.route("/")
@login_required
def listar():
    q=_clean(request.args.get("q")); page=max(request.args.get("page",1,type=int),1)
    consulta=Persona.query
    if q:
        consulta=consulta.filter(or_(Persona.numero_documento.ilike(f"%{q}%"), Persona.nombre_completo.ilike(f"%{q}%")))
        registrar_auditoria("BUSQUEDA","HISTORIAS",f"Persona: {q[:100]}")
    personas=consulta.order_by(Persona.nombre_completo).paginate(page=page,per_page=25,error_out=False)
    return render_template("historias/lista.html", personas=personas)

@historias_bp.route("/<int:id>")
@login_required
def ver(id):
    persona=Persona.query.get_or_404(id)
    return render_template("historias/detalle.html", persona=persona)

@historias_bp.route("/nueva", methods=["GET","POST"])
@login_required
def nueva():
    tipos=TipoDocumento.query.filter_by(activo=True).all()
    if request.method=="POST":
        tipo_id=request.form.get("tipo_documento_id",type=int); documento=_clean(request.form.get("numero_documento")); nombre=_clean(request.form.get("nombre_completo")).upper()
        if not tipo_id or not documento or not nombre:
            flash("Tipo de documento, identificación y nombre son obligatorios.","danger")
        elif Persona.query.filter_by(tipo_documento_id=tipo_id, numero_documento=documento).first():
            flash("Ya existe una persona con ese documento. Ingrese y agregue una nueva carpeta física.","warning")
        else:
            p=Persona(tipo_documento_id=tipo_id, numero_documento=documento, nombre_completo=nombre, creada_por_id=current_user.id)
            db.session.add(p); db.session.commit(); registrar_auditoria("CREAR","PERSONAS",f"{documento} - {nombre}")
            flash("Persona creada. Ahora puede agregar su carpeta física.","success")
            return redirect(url_for("historias.ver",id=p.id))
    return render_template("historias/persona_form.html", tipos=tipos, persona=None)

@historias_bp.route("/<int:id>/editar", methods=["GET","POST"])
@login_required
def editar(id):
    p=Persona.query.get_or_404(id); tipos=TipoDocumento.query.filter_by(activo=True).all()
    if request.method=="POST":
        doc=_clean(request.form.get("numero_documento")); nombre=_clean(request.form.get("nombre_completo")).upper(); tipo_id=request.form.get("tipo_documento_id",type=int)
        dup=Persona.query.filter(Persona.id!=p.id, Persona.tipo_documento_id==tipo_id, Persona.numero_documento==doc).first()
        if dup: flash("Ese documento ya corresponde a otra persona.","danger")
        elif not nombre or not doc: flash("Documento y nombre son obligatorios.","danger")
        else:
            p.tipo_documento_id=tipo_id; p.numero_documento=doc; p.nombre_completo=nombre; db.session.commit(); registrar_auditoria("EDITAR","PERSONAS",doc)
            flash("Persona actualizada.","success"); return redirect(url_for("historias.ver",id=p.id))
    return render_template("historias/persona_form.html", tipos=tipos, persona=p)

@historias_bp.route("/<int:persona_id>/carpetas/nueva", methods=["GET","POST"])
@login_required
def nueva_carpeta(persona_id):
    persona=Persona.query.get_or_404(persona_id); unidades=UnidadConservacion.query.filter_by(activo=True).all(); centros=CentroTrabajo.query.filter_by(activo=True).all()
    if request.method=="POST":
        try: consecutivo=int(request.form.get("consecutivo_carpeta","0"))
        except: consecutivo=0
        fecha=_parse_date(request.form.get("fecha_ingreso","")); centro_id=request.form.get("centro_id",type=int); unidad_id=request.form.get("unidad_conservacion_id",type=int)
        if consecutivo<1 or not fecha or not centro_id or not unidad_id:
            flash("Complete consecutivo, fecha, centro y unidad de conservación.","danger")
        elif fecha > date.today(): flash("La fecha de ingreso no puede ser futura.","danger")
        elif CarpetaFisica.query.filter_by(consecutivo_carpeta=consecutivo).first(): flash("Ese consecutivo ya está asignado.","danger")
        else:
            centro=db.session.get(CentroTrabajo,centro_id)
            c=CarpetaFisica(identificador_unico=f"{centro.codigo}-{persona.id}-{consecutivo}", persona_id=persona.id,
                unidad_conservacion_id=unidad_id, consecutivo_carpeta=consecutivo, fecha_ingreso=fecha,
                estado=request.form.get("estado","activo"), centro_id=centro_id, empresa="MHC", creada_por_id=current_user.id)
            db.session.add(c); db.session.flush(); db.session.add(ConsecutivoCarpeta(numero=consecutivo,disponible=False,carpeta_id=c.id)); db.session.commit()
            registrar_auditoria("CREAR","CARPETAS",f"Persona {persona.numero_documento}; carpeta {consecutivo}")
            flash("Carpeta física creada.","success"); return redirect(url_for("historias.ver",id=persona.id))
    return render_template("historias/carpeta_form.html", persona=persona, carpeta=None, unidades=unidades, centros=centros)

@historias_bp.route("/carpetas/<int:id>/editar", methods=["GET","POST"])
@login_required
def editar_carpeta(id):
    c=CarpetaFisica.query.get_or_404(id); unidades=UnidadConservacion.query.filter_by(activo=True).all(); centros=CentroTrabajo.query.filter_by(activo=True).all()
    if request.method=="POST":
        fecha=_parse_date(request.form.get("fecha_ingreso",""));
        if not fecha or fecha>date.today(): flash("Fecha de ingreso inválida o futura.","danger")
        else:
            c.fecha_ingreso=fecha; c.centro_id=request.form.get("centro_id",type=int); c.unidad_conservacion_id=request.form.get("unidad_conservacion_id",type=int); c.estado=request.form.get("estado","activo")
            db.session.commit(); registrar_auditoria("EDITAR","CARPETAS",f"Carpeta {c.consecutivo_carpeta}")
            flash("Carpeta actualizada.","success"); return redirect(url_for("historias.ver",id=c.persona_id))
    return render_template("historias/carpeta_form.html", persona=c.persona, carpeta=c, unidades=unidades, centros=centros)

@historias_bp.route("/carpetas/<int:id>/archivar", methods=["POST"])
@login_required
@roles_required("admin","auditor")
def archivar(id):
    c=CarpetaFisica.query.get_or_404(id)
    if c.prestamo_activo: flash("No puede archivar una carpeta prestada.","danger")
    else:
        c.archivada=True; c.consecutivo_archivo=c.consecutivo_archivo or f"ARCH-{datetime.utcnow():%Y}-{c.id:06d}"
        cupo=ConsecutivoCarpeta.query.filter_by(carpeta_id=c.id).first()
        if cupo: cupo.disponible=True; cupo.carpeta_id=None
        db.session.commit(); registrar_auditoria("ARCHIVAR","CARPETAS",f"Carpeta {c.consecutivo_carpeta}"); flash("Carpeta archivada.","success")
    return redirect(url_for("historias.ver",id=c.persona_id))

@historias_bp.route("/archivadas")
@login_required
@roles_required("admin","auditor")
def archivadas():
    page=max(request.args.get("page",1,type=int),1)
    carpetas=CarpetaFisica.query.filter_by(archivada=True).order_by(CarpetaFisica.consecutivo_carpeta).paginate(page=page,per_page=25,error_out=False)
    return render_template("historias/archivadas.html", carpetas=carpetas)

@historias_bp.route("/consecutivos")
@login_required
def consecutivos():
    page=max(request.args.get("page",1,type=int),1); estado=request.args.get("estado","todos")
    q=ConsecutivoCarpeta.query
    if estado=="disponibles": q=q.filter_by(disponible=True)
    elif estado=="asignados": q=q.filter_by(disponible=False)
    datos=q.order_by(ConsecutivoCarpeta.numero).paginate(page=page,per_page=25,error_out=False)
    return render_template("historias/consecutivos.html",datos=datos,estado=estado,siguiente=(db.session.query(func.max(ConsecutivoCarpeta.numero)).scalar() or 0)+1)
