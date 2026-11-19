# CRM Básico

Sistema de gestión de clientes para uso comercial, desarrollado con Django como primera tarea proyecto del módulo de Django del máster Full Stack.

## Funcionalidades

- **CRUD de clientes** con paginación.
- **CRUD de interacciones** (llamadas, emails, reuniones…) desde la ficha de cada cliente.
- **Relación comercial–cliente con roles:**
  - Los comerciales solo ven y gestionan sus propios clientes.
  - Los responsables ven todos los clientes, pueden reasignarlos y eliminarlos.
- **Buscador** por nombre, apellidos, email o empresa.
- **Estadísticas**: totales, interacciones por tipo y clientes por comercial.
- **Exportación** del listado (respetando la búsqueda) a CSV y Excel.

## Tecnologías

- Python 3 y Django
- SQLite
- Bootstrap 5 y Chart.js
- openpyxl (exportación a Excel)
- django-debug-toolbar y django-extensions (desarrollo)

## Modelos

- **User**: usuario personalizado con el campo `is_manager` (responsable comercial).
- **Company**: empresa del cliente.
- **Client**: cliente, con empresa y comercial asignado.
- **Interaction**: contacto con un cliente (tipo, fecha, resumen, notas y quién lo registró).

## Instalación

```bash
git clone <url-del-repositorio>
cd proyecto-crm-basico
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre http://127.0.0.1:8000/ e inicia sesión.

Para crear comerciales y responsables, entra en `/admin/` y marca la casilla **responsable comercial** en los usuarios que deban ver todos los clientes.

## Tests

```bash
python manage.py test crm
```

Los tests comprueban las reglas de acceso, la visibilidad por comercial, la asignación automática, el buscador y la creación, edición y eliminación de interacciones.

## Decisiones de diseño

- **Lógica de negocio en los modelos**: la visibilidad (`visible_to`) y la búsqueda (`search`) son métodos de un QuerySet personalizado, reutilizados en el listado, la exportación y las estadísticas.
- **404 frente a 403**: un cliente ajeno devuelve 404 para no revelar su existencia; borrar sin permiso devuelve 403.
- **Optimización de consultas** con `select_related` y `annotate` para evitar el problema N+1.

## Mejoras posibles

- Búsqueda sin distinguir tildes (PostgreSQL con `unaccent`).
- Protección frente a inyección de fórmulas en la exportación CSV.
- Grupos y permisos de Django si se necesitaran más roles.
