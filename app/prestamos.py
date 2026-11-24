from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, exists
from . import db
from .models import Persona, CarpetaFisica, Prestamo
from .security import registrar_auditoria, roles_required
prestamos_bp=Blueprint("prestamos",__name__)

@prestamos_bp.route("/")
@login_required
def listar():
    page=max(request.args.get("page",1,type=int),1); q=(request.args.get("q") or "").strip(); estado=request.args.get("estado","")
    consulta=Prestamo.query.join(CarpetaFisica).join(Persona)
    if q: consulta=consulta.filter(or_(Persona.nombre_completo.ilike(f"%{q}%"),Persona.numero_documento.ilike(f"%{q}%"),Prestamo.solicitante.ilike(f"%{q}%"),Prestamo.area_solicitante.ilike(f"%{q}%")))
    if estado=="vencidos": consulta=consulta.filter(Prestamo.estado=="prestado",Prestamo.fecha_devolucion_prevista<date.today())
    elif estado in {"prestado","devuelto"}: consulta=consulta.filter(Prestamo.estado==estado)
    prestamos=consulta.order_by(Prestamo.fecha_prestamo.desc()).paginate(page=page,per_page=25,error_out=False)
    return render_template("prestamos/lista.html",prestamos=prestamos,estado=estado)

@prestamos_bp.route("/nuevo",methods=["GET","POST"])
@login_required
def nuevo():
    carpeta_id=request.args.get("carpeta_id",type=int)
    if request.method=="POST":
        c=CarpetaFisica.query.get_or_404(request.form.get("carpeta_id",type=int) or 0)
        try: fecha_prevista=datetime.strptime(request.form.get("fecha_devolucion_prevista",""),"%Y-%m-%d").date()
        except ValueError: fecha_prevista=None
        if c.archivada or c.estado!="activo" or c.prestamo_activo:
            flash("La carpeta no está disponible para préstamo.","danger")
        elif not fecha_prevista:
            flash("La fecha prevista de devolución no es válida.","danger")
        else:
            p=Prestamo(carpeta_id=c.id,solicitante=request.form["solicitante"].strip().upper(),area_solicitante=request.form["area_solicitante"].strip().upper(),motivo=request.form["motivo"].strip(),fecha_devolucion_prevista=fecha_prevista,observaciones_salida=request.form.get("observaciones_salida","").strip(),entregado_por_id=current_user.id,estado="prestado")
            db.session.add(p); db.session.commit(); registrar_auditoria("PRESTAR","PRESTAMOS",f"Carpeta {c.consecutivo_carpeta} - {c.persona.numero_documento}")
            flash("Préstamo registrado.","success"); return redirect(url_for("prestamos.listar"))
    return render_template("prestamos/form.html",carpeta_id=carpeta_id,fecha_sugerida=(date.today()+timedelta(days=5)).isoformat())

@prestamos_bp.route("/<int:id>/devolver",methods=["GET","POST"])
@login_required
def devolver(id):
    p=Prestamo.query.get_or_404(id)
    if request.method=="POST" and p.estado=="prestado":
        p.estado="devuelto"; p.fecha_devolucion_real=datetime.utcnow(); p.recibido_por_id=current_user.id; p.observaciones_devolucion=request.form.get("observaciones_devolucion","").strip(); db.session.commit(); registrar_auditoria("DEVOLVER","PRESTAMOS",f"Carpeta {p.carpeta.consecutivo_carpeta}"); flash("Devolución registrada.","success"); return redirect(url_for("prestamos.listar"))
    return render_template("prestamos/devolver.html",prestamo=p)

@prestamos_bp.route("/<int:id>/eliminar",methods=["POST"])
@login_required
@roles_required("admin","auditor")
def eliminar(id):
    p=Prestamo.query.get_or_404(id)
    if p.estado=="prestado": flash("Primero debe registrar la devolución.","danger")
    else: db.session.delete(p); db.session.commit(); flash("Registro eliminado.","success")
    return redirect(url_for("prestamos.listar"))

@prestamos_bp.route("/buscar-carpetas")
@login_required
def buscar_carpetas():
    q=(request.args.get("q") or "").strip()
    if len(q)<2: return jsonify([])
    carpetas=(CarpetaFisica.query.join(Persona).filter(CarpetaFisica.estado=="activo",CarpetaFisica.archivada.is_(False),or_(Persona.nombre_completo.ilike(f"%{q}%"),Persona.numero_documento.ilike(f"%{q}%"),db.cast(CarpetaFisica.consecutivo_carpeta,db.String).ilike(f"%{q}%"))).order_by(Persona.nombre_completo).limit(15).all())
    return jsonify([{"id":c.id,"consecutivo":c.consecutivo_carpeta,"nombre":c.persona.nombre_completo,"documento":c.persona.numero_documento,"disponible":not bool(c.prestamo_activo)} for c in carpetas if not c.prestamo_activo])
