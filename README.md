# Sistema de Historias Laborales V2

Incluye paginación, Dashboard visible, usuario y rol en menú, protección de auditores, CRUD de centros, código automático de centro, consecutivos globales e ilimitados, liberación al retirar y modales centrados.

## Actualización de base de datos para pruebas

La estructura cambió. Elimine la base anterior y vuelva a crearla:

```bash
rm -f historias_laborales.db instance/historias_laborales.db
python -m app.seed
python run.py
```

Usuario: auditor  
Contraseña temporal: Temporal123

## Módulo de préstamos de historias físicas

Esta versión incorpora:

- Registro de préstamos de carpetas físicas.
- Control de solicitante, área, motivo y fecha prevista de devolución.
- Estados prestado, vencido y devuelto.
- Registro de devolución y observaciones.
- Indicador de disponibilidad en la vista de historias laborales.
- Bloqueo de préstamos duplicados para una misma carpeta.
- Bloqueo de retiro, archivo o eliminación mientras exista un préstamo activo.
- Auditoría de préstamos, devoluciones, búsquedas y eliminaciones.
- Reporte CSV de préstamos.

El sistema ya no solicita cargar archivos PDF. El campo antiguo se conserva únicamente para compatibilidad con la base de datos existente.

Al iniciar la aplicación, `db.create_all()` creará automáticamente la nueva tabla de préstamos sin borrar los registros existentes.
