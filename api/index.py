from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Añadir el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la app existente
from app.main import app

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel necesita esta variable para ejecutar la aplicación
app = app 