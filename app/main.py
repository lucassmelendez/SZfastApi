from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import clientes, empleados

app = FastAPI(
    title="API de gestión de SpinZone",
    version="1.0.0",
    description="API para gestionar clientes y empleados usando FastAPI y Supabase"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sz-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
