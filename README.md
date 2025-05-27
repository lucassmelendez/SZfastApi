# 🚀 API de Gestión de SpinZone con FastAPI y Supabase

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0+-blue.svg)
![Supabase](https://img.shields.io/badge/Supabase-2.15.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.7+-yellow.svg)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black.svg)](https://szfast-api.vercel.app)

Una API REST robusta para la gestión de clientes, empleados, pedidos y productos en el sistema SpinZone. Desarrollada con FastAPI como framework web y Supabase como base de datos.

## 📋 Índice

- [✨ Características](#-características)
- [🔧 Requisitos](#-requisitos)
- [🛠️ Instalación](#️-instalación)
- [⚙️ Configuración de Supabase](#️-configuración-de-supabase)
- [🗄️ Estructura del Proyecto](#️-estructura-del-proyecto)
- [📊 Estructura de la Base de Datos](#-estructura-de-la-base-de-datos)
- [▶️ Ejecución](#️-ejecución)
- [📝 Documentación de la API](#-documentación-de-la-api)
- [🔌 Endpoints](#-endpoints)
- [🚢 Despliegue en Vercel](#-despliegue-en-vercel)
- [🧪 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)

## ✨ Características

- **Gestión de Clientes**: Registro, consulta, actualización y eliminación de clientes.
- **Gestión de Empleados**: Administración completa de información de empleados.
- **Sistema de Pedidos**: Creación y seguimiento de pedidos con sus productos asociados.
- **Autenticación**: Sistema de login para clientes y empleados.
- **Documentación Automática**: Interfaz Swagger y ReDoc para explorar y probar la API.
- **Despliegue Serverless**: Configurado para despliegue en Vercel.

## 🔧 Requisitos

- Python 3.7 o superior
- FastAPI 0.115.0 o superior
- Supabase 2.15.0 o superior
- Pydantic 2.0.0 o superior
- Uvicorn 0.26.0 o superior
- Starlette 0.35.0 o superior
- Python-dotenv 1.0.0 o superior (para migraciones)

## 🛠️ Instalación

1. **Clona este repositorio**:
   ```bash
   git clone https://github.com/lucassmelendez/SZfastApi.git
   cd SZfastApi
   ```

2. **Crea un entorno virtual** (recomendado):
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate

   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**:
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-api-key-de-supabase
   ```

   También puedes usar el script de configuración:
   ```bash
   python scripts/setup_env.py
   ```

## ⚙️ Configuración de Supabase

1. Crea una cuenta en [Supabase](https://supabase.com/)
2. Crea un nuevo proyecto
3. En el SQL Editor, ejecuta el script ubicado en:
   ```bash
   # Para estructura completa
   scripts/init_supabase_tables.sql
   
   # O para estructura básica
   scripts/init_supabase.sql
   ```

4. Obtén la URL y API Key desde la sección "Settings" > "API" del proyecto en Supabase
5. Actualiza el archivo `.env` con tus credenciales

## 🗄️ Estructura del Proyecto

```
SZfastApi/
├── api/                    # Punto de entrada para despliegue serverless
│   └── index.py            # Handler principal para Vercel
├── app/                    # Código principal de la aplicación
│   ├── main.py             # Punto de entrada de la aplicación FastAPI
│   ├── database.py         # Configuración y conexión a Supabase
│   └── routers/            # Endpoints organizados por recursos
│       ├── clientes.py     # Rutas para gestión de clientes
│       ├── empleados.py    # Rutas para gestión de empleados
│       ├── pedidos.py      # Rutas para gestión de pedidos
│       └── pedido_producto.py # Rutas para productos en pedidos
├── scripts/                # Scripts de utilidad
│   ├── init_supabase_tables.sql   # Script SQL para crear tablas
│   ├── init_supabase.sql          # Script SQL básico
│   ├── setup_env.py               # Configuración de variables de entorno
│   ├── iniciar_app.py             # Script para iniciar la aplicación
│   └── verificar_vercel.py        # Verificación de despliegue en Vercel
├── .env                    # Variables de entorno (no incluido en el repositorio)
├── .gitignore              # Archivos y directorios ignorados por git
├── requirements.txt        # Dependencias del proyecto
├── vercel.json             # Configuración para despliegue en Vercel
└── README.md               # Documentación del proyecto
```

## 📊 Estructura de la Base de Datos

El sistema utiliza las siguientes tablas principales:

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

### Tabla `pedido` y `pedido_producto`
Revisa el script SQL para detalles sobre las tablas de pedidos y productos.

## ▶️ Ejecución

### Desarrollo Local

Para ejecutar la API en modo desarrollo:

```bash
# Usando uvicorn directamente
uvicorn app.main:app --reload

# O usando el script de inicio
python scripts/iniciar_app.py
```

La API estará disponible en [http://localhost:8000](http://localhost:8000)

### Testing

Para verificar la configuración de Vercel antes del despliegue:

```bash
python scripts/verificar_vercel.py
```

## 📝 Documentación de la API

La documentación automática de la API estará disponible en:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔌 Endpoints

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

### Pedidos
- `GET /pedidos`: Obtiene todos los pedidos
- `GET /pedidos/{id_pedido}`: Obtiene un pedido por su ID
- `POST /pedidos`: Crea un nuevo pedido
- `PUT /pedidos/{id_pedido}`: Actualiza un pedido existente
- `DELETE /pedidos/{id_pedido}`: Elimina un pedido

### Pedidos-Productos
- `GET /pedido-producto`: Obtiene todos los productos en pedidos
- `GET /pedido-producto/{id_pedido_producto}`: Obtiene un producto específico en un pedido
- `POST /pedido-producto`: Agrega un producto a un pedido
- `PUT /pedido-producto/{id_pedido_producto}`: Actualiza un producto en un pedido
- `DELETE /pedido-producto/{id_pedido_producto}`: Elimina un producto de un pedido

### Usuarios (Deprecated)
- `GET /usuarios`: Obtiene todos los usuarios
- `GET /usuarios/{rut}`: Obtiene un usuario por su RUT
- `POST /usuarios`: Agrega un nuevo usuario
- `PUT /usuarios/{rut}`: Actualiza los datos de un usuario
- `PATCH /usuarios/{rut}`: Actualiza parcialmente los datos de un usuario
- `DELETE /usuarios/{rut}`: Elimina un usuario

## 🚢 Despliegue en Vercel

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

5. Tu API estará disponible en la URL proporcionada por Vercel (ejemplo: [https://szfast-api.vercel.app](https://szfast-api.vercel.app))

### Consideraciones para el despliegue en Vercel

- Vercel ofrece funciones sin servidor, por lo que cada solicitud a la API iniciará una nueva instancia de la función
- Las conexiones a la base de datos deben establecerse para cada solicitud
- Hay límites en el tiempo de ejecución (no adecuado para operaciones de larga duración)
- Las funciones sin servidor de Vercel tienen un límite de 50MB para el tamaño del paquete, incluyendo dependencias

## 🧪 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Realiza tus cambios
4. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
5. Push a la rama (`git push origin feature/amazing-feature`)
6. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia [MIT](https://opensource.org/licenses/MIT).

---

Desarrollado por [Lucas Meléndez](https://github.com/lucassmelendez) 