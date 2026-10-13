# HISLA - versión de pruebas Persona → Carpetas

Esta versión reorganiza el modelo para que una persona identificada por tipo + número de documento pueda tener una o varias carpetas físicas.

## Datos precargados
- 1.824 personas únicas.
- 1.910 carpetas físicas.
- 86 personas tienen dos carpetas físicas.
- Los 1.910 consecutivos del Excel son únicos.

## Criterios usados para esta prueba
- Las filas sin Centro_trabajo se asociaron a `Mario Huertas Cotes` por pertenecer a Empresa MHC.
- Las 88 filas con `Oficina Principal` se asociaron a un centro nuevo con ese nombre.
- Se detectó una fecha de ingreso futura (19/11/2027) para CRUZ ESCOBAR DEYCI YANETH. En la base de pruebas se ajustó temporalmente a 13/10/2026 y el valor original quedó en `fecha_ingreso_origen` para que sea visible y se corrija antes de producción.
- El tipo de documento se cargó como CC para este listado de prueba.

## Flujo nuevo
Historias → lista de personas → Ver carpetas → lista de carpetas físicas.
El préstamo se registra sobre una carpeta física concreta, no sobre la persona.

## Ejecutar localmente
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
Abrir http://127.0.0.1:5000

La base `historias_laborales.db` ya viene precargada.
