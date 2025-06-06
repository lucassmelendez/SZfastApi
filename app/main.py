from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import clientes, empleados, pedidos, pedido_producto
from app.logging_config import configure_logging

# Configurar el logging al inicio de la aplicación
configure_logging()

app = FastAPI(
    title="API de gestión de SpinZone",
    version="1.0.0",
    description="API para gestionar clientes y empleados usando FastAPI y Supabase"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sz-frontend.vercel.app", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(empleados.router)
app.include_router(pedidos.router)
app.include_router(pedido_producto.router)

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido a la API de gestión de SpinZone",
        "documentacion": "/docs",
        "endpoints": [
            {"ruta": "/clientes", "descripcion": "Gestión de clientes"},
            {"ruta": "/empleados", "descripcion": "Gestión de empleados"},
            {"ruta": "/pedidos", "descripcion": "Gestión de pedidos"},
            {"ruta": "/pedido-producto", "descripcion": "Gestión de productos en pedidos"}
        ]
    }
