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

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**:
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-api-key-de-supabase
   ```

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
│   ├── iniciar_app.py             # Script para iniciar la aplicación
├── .env                    # Variables de entorno (no incluido en el repositorio)
├── requirements.txt        # Dependencias del proyecto
├── vercel.json             # Configuración para despliegue en Vercel
└── README.md               # Documentación del proyecto
```

## 📊 Estructura de la Base de Datos

El sistema utiliza las siguientes tablas principales:

### Tabla `rol`
- `id_rol`: ID único del rol (PK)
- `nombre_rol`: Nombre del rol

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

### Tabla `pedido`
- `id_pedido`: ID único del pedido (PK)
- `fecha_pedido`: Fecha de creación del pedido
- `estado`: Estado actual del pedido
- `total`: Monto total del pedido
- `id_cliente`: Referencia al cliente que realizó el pedido (FK)

### Tabla `pedido_producto`
- `id_pedido_producto`: ID único de la relación pedido-producto (PK)
- `id_pedido`: Referencia al pedido (FK)
- `id_producto`: Referencia al producto (FK)
- `cantidad`: Cantidad del producto en el pedido
- `precio_unitario`: Precio unitario del producto al momento de la compra
- `subtotal`: Subtotal (cantidad * precio_unitario)

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

## 📝 Documentación de la API

La documentación automática de la API estará disponible en:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

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
     vercel --prod
     ```

5. URL de Produccion: [https://szfast-api.vercel.app](https://szfast-api.vercel.app))
