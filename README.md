# API de Gestión de SpinZone con FastAPI y Supabase

Esta es una API para gestionar clientes y empleados utilizando FastAPI como framework web y Supabase como base de datos.

## Requisitos

- Python 3.7 o superior
- FastAPI
- Supabase

## Instalación

1. Clona este repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

2. Instala las dependencias:
```bash
pip install fastapi uvicorn python-dotenv supabase pydantic starlette
```

3. Crea un archivo `.env` en la raíz del proyecto con la siguiente información:
```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-api-key-de-supabase
```

## Configuración de Supabase

1. Crea una cuenta en [Supabase](https://supabase.com/)
2. Crea un nuevo proyecto
3. En el SQL Editor, ejecuta el script ubicado en `scripts/init_supabase_tables.sql` para crear las tablas necesarias

4. Obtén la URL y API Key de tu proyecto desde la configuración del proyecto en Supabase
5. Actualiza el archivo `.env` con tus credenciales

## Estructura de la base de datos

El sistema utiliza las siguientes tablas:

### Tabla `rol`
- `id_rol`: ID único del rol (PK)
- `nombre_rol`: Nombre del rol

### Tabla `informe`
- `id_informe`: ID único del informe (PK)
- `descripcion`: Descripción del informe

### Tabla `cliente`
- `id_cliente`: ID único del cliente (PK)
- `nombre`: Nombre del cliente
- `apellido`: Apellido del cliente
- `correo`: Correo electrónico (único)
- `telefono`: Número de teléfono
- `direccion`: Dirección física
- `id_rol`: Referencia a la tabla rol (FK)
- `rut`: RUT del cliente
- `contrasena`: Contraseña del cliente

### Tabla `empleado`
- `id_empleado`: ID único del empleado (PK)
- `nombre`: Nombre del empleado
- `apellido`: Apellido del empleado
- `rut`: RUT del empleado
- `correo`: Correo electrónico (único)
- `contrasena`: Contraseña del empleado
- `direccion`: Dirección física
- `telefono`: Número de teléfono
- `rol_id`: Referencia a la tabla rol (FK)
- `informe_id`: Referencia a la tabla informe (FK)

## Ejecución

Para ejecutar la API en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en http://localhost:8000

## Documentación de la API

La documentación automática de la API estará disponible en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Clientes
- `GET /clientes`: Obtiene todos los clientes
- `GET /clientes/{id_cliente}`: Obtiene un cliente por su ID
- `GET /clientes/rut/{rut}`: Obtiene un cliente por su RUT
- `POST /clientes`: Agrega un nuevo cliente
- `POST /clientes/login`: Realiza inicio de sesión de cliente
- `PUT /clientes/{id_cliente}`: Actualiza los datos de un cliente
- `DELETE /clientes/{id_cliente}`: Elimina un cliente

### Empleados
- `GET /empleados`: Obtiene todos los empleados
- `GET /empleados/{id_empleado}`: Obtiene un empleado por su ID
- `GET /empleados/rut/{rut}`: Obtiene un empleado por su RUT
- `POST /empleados`: Agrega un nuevo empleado
- `POST /empleados/login`: Realiza inicio de sesión de empleado
- `PUT /empleados/{id_empleado}`: Actualiza los datos de un empleado
- `DELETE /empleados/{id_empleado}`: Elimina un empleado

### Usuarios (Deprecated)
- `GET /usuarios`: Obtiene todos los usuarios
- `GET /usuarios/{rut}`: Obtiene un usuario por su RUT
- `POST /usuarios`: Agrega un nuevo usuario
- `PUT /usuarios/{rut}`: Actualiza los datos de un usuario
- `PATCH /usuarios/{rut}`: Actualiza parcialmente los datos de un usuario
- `DELETE /usuarios/{rut}`: Elimina un usuario

## Despliegue en Vercel

Esta API está configurada para ser desplegada en Vercel. Para desplegarla, sigue estos pasos:

1. Asegúrate de tener una cuenta en [Vercel](https://vercel.com/)
2. Instala la CLI de Vercel (opcional):
```bash
npm install -g vercel
```

3. Configura las variables de entorno en Vercel:
   - Ve al panel de control de Vercel
   - Selecciona tu proyecto
   - Ve a "Settings" > "Environment Variables"
   - Añade las variables `SUPABASE_URL` y `SUPABASE_KEY` con los valores de tu proyecto de Supabase

4. Despliega tu proyecto:
   - Usando la CLI (desde la raíz del proyecto):
   ```bash
   vercel
   ```
   - O conecta tu repositorio a Vercel y configura el despliegue automático

5. Tu API estará disponible en la URL proporcionada por Vercel

### Consideraciones para el despliegue en Vercel

- Vercel ofrece funciones sin servidor, por lo que cada solicitud a la API iniciará una nueva instancia de la función
- Las conexiones a la base de datos deben establecerse para cada solicitud
- Hay límites en el tiempo de ejecución (no adecuado para operaciones de larga duración)
- Las funciones sin servidor de Vercel tienen un límite de 50MB para el tamaño del paquete, incluyendo dependencias 