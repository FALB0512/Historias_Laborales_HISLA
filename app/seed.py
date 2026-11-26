from app import create_app, db
from app.models import Usuario, TipoDocumento, UnidadConservacion


def sembrar_datos():
    if not Usuario.query.filter_by(username="auditor").first():
        u = Usuario(nombre="Auditor Inicial", username="auditor",
                    email="auditor@local.test", rol="auditor",
                    debe_cambiar_password=True)
        u.set_password("Temporal123")
        db.session.add(u)

    documentos = [("CC", "Cédula de ciudadanía"), ("CE", "Cédula de extranjería"),
                  ("PAS", "Pasaporte"), ("PPT", "Permiso por Protección Temporal")]
    for codigo, nombre in documentos:
        if not TipoDocumento.query.filter_by(codigo=codigo).first():
            db.session.add(TipoDocumento(codigo=codigo, nombre=nombre))

    for nombre in ["Carpeta", "Caja", "Expediente", "Legajo"]:
        if not UnidadConservacion.query.filter_by(nombre=nombre).first():
            db.session.add(UnidadConservacion(nombre=nombre))

    db.session.commit()
    print("Datos iniciales creados. Usuario: auditor / Clave: Temporal123")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        sembrar_datos()
