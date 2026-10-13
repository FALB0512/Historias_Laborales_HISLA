from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="asistente")
    activo = db.Column(db.Boolean, default=True, nullable=False)
    debe_cambiar_password = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class CentroTrabajo(db.Model):
    __tablename__ = "centro_trabajo"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    carpetas = db.relationship("CarpetaFisica", backref="centro", lazy=True)

class TipoDocumento(db.Model):
    __tablename__ = "tipo_documento"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

class UnidadConservacion(db.Model):
    __tablename__ = "unidad_conservacion"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

class Persona(db.Model):
    __tablename__ = "persona"
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento_id = db.Column(db.Integer, db.ForeignKey("tipo_documento.id"), nullable=False)
    numero_documento = db.Column(db.String(30), nullable=False, index=True)
    nombre_completo = db.Column(db.String(180), nullable=False, index=True)
    creada_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizada_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tipo_documento = db.relationship("TipoDocumento")
    creada_por = db.relationship("Usuario")
    carpetas = db.relationship("CarpetaFisica", back_populates="persona", lazy=True, cascade="all, delete-orphan", order_by="CarpetaFisica.consecutivo_carpeta.asc()")
    __table_args__ = (db.UniqueConstraint("tipo_documento_id", "numero_documento", name="uq_persona_documento"),)
    @property
    def carpetas_activas(self): return [c for c in self.carpetas if not c.archivada]
    @property
    def cantidad_carpetas(self): return len(self.carpetas)
    @property
    def tiene_multiples_carpetas(self): return len(self.carpetas) > 1

class CarpetaFisica(db.Model):
    __tablename__ = "carpeta_fisica"
    id = db.Column(db.Integer, primary_key=True)
    identificador_unico = db.Column(db.String(60), unique=True, nullable=False, index=True)
    persona_id = db.Column(db.Integer, db.ForeignKey("persona.id"), nullable=False, index=True)
    unidad_conservacion_id = db.Column(db.Integer, db.ForeignKey("unidad_conservacion.id"), nullable=False)
    consecutivo_carpeta = db.Column(db.Integer, unique=True, nullable=False, index=True)
    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_ingreso_origen = db.Column(db.String(20))
    fecha_inicio_contrato = db.Column(db.Date)
    fecha_retiro = db.Column(db.Date)
    estado = db.Column(db.String(15), nullable=False, default="activo", index=True)
    centro_id = db.Column(db.Integer, db.ForeignKey("centro_trabajo.id"), nullable=False)
    archivada = db.Column(db.Boolean, default=False, nullable=False, index=True)
    consecutivo_archivo = db.Column(db.String(40), unique=True)
    serie = db.Column(db.String(120))
    empresa = db.Column(db.String(50))
    folios = db.Column(db.Integer)
    estado_vinculo = db.Column(db.String(50))
    archivo_gestion = db.Column(db.String(180))
    estado_transferencia = db.Column(db.String(180))
    source_id = db.Column(db.String(50))
    creada_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizada_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    persona = db.relationship("Persona", back_populates="carpetas")
    unidad_conservacion = db.relationship("UnidadConservacion")
    creada_por = db.relationship("Usuario")
    prestamos = db.relationship("Prestamo", back_populates="carpeta", lazy=True, cascade="all, delete-orphan", order_by="Prestamo.fecha_prestamo.desc()")
    @property
    def prestamo_activo(self): return next((p for p in self.prestamos if p.estado == "prestado"), None)
    @property
    def disponibilidad_fisica(self): return "Prestada" if self.prestamo_activo else "Disponible"

class ConsecutivoCarpeta(db.Model):
    __tablename__ = "consecutivo_carpeta"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    disponible = db.Column(db.Boolean, default=True, nullable=False)
    carpeta_id = db.Column(db.Integer, db.ForeignKey("carpeta_fisica.id"), nullable=True, unique=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    carpeta = db.relationship("CarpetaFisica")

class Prestamo(db.Model):
    __tablename__ = "prestamo"
    id = db.Column(db.Integer, primary_key=True)
    carpeta_id = db.Column(db.Integer, db.ForeignKey("carpeta_fisica.id"), nullable=False, index=True)
    solicitante = db.Column(db.String(160), nullable=False, index=True)
    area_solicitante = db.Column(db.String(140), nullable=False, index=True)
    motivo = db.Column(db.String(300), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    fecha_devolucion_prevista = db.Column(db.Date, nullable=False, index=True)
    fecha_devolucion_real = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default="prestado", nullable=False, index=True)
    observaciones_salida = db.Column(db.Text)
    observaciones_devolucion = db.Column(db.Text)
    entregado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    recibido_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    carpeta = db.relationship("CarpetaFisica", back_populates="prestamos")
    entregado_por = db.relationship("Usuario", foreign_keys=[entregado_por_id])
    recibido_por = db.relationship("Usuario", foreign_keys=[recibido_por_id])
    @property
    def vencido(self): return self.estado == "prestado" and self.fecha_devolucion_prevista < date.today()

class Auditoria(db.Model):
    __tablename__ = "auditoria"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    accion = db.Column(db.String(40), nullable=False)
    modulo = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.Text)
    ip = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    usuario = db.relationship("Usuario")
