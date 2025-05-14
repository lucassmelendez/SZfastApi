from fastapi import FastAPI
from app.routers import usuarios, clientes, empleados

app = FastAPI(
    title="API de gestión de SpinZone",
    version="1.0.0",
    description="API para gestionar clientes y empleados usando FastAPI y Supabase"
)

# Incluir rutas
app.include_router(clientes.router)
app.include_router(empleados.router)

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido a la API de gestión de SpinZone",
        "documentacion": "/docs",
        "endpoints": [
            {"ruta": "/clientes", "descripcion": "Gestión de clientes"},
            {"ruta": "/empleados", "descripcion": "Gestión de empleados"}
        ]
    }
