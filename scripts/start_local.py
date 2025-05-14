#!/usr/bin/env python
"""
Script para iniciar la API localmente.
Este script configura el entorno y luego inicia el servidor uvicorn.
"""
import os
import sys
import subprocess
from pathlib import Path

# Obtener la ruta raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.absolute()

def setup_env():
    """Configura las variables de entorno para desarrollo."""
    print("Configurando variables de entorno para desarrollo...")
    
    # Valores de ejemplo para desarrollo
    os.environ["SUPABASE_URL"] = "https://ejemplo.supabase.co"
    os.environ["SUPABASE_KEY"] = "ejemplo-api-key"
    
    print("Variables de entorno configuradas temporalmente para desarrollo.")

def start_server():
    """Inicia el servidor uvicorn."""
    print("Iniciando servidor uvicorn...")
    
    # Cambiar al directorio raíz del proyecto
    os.chdir(ROOT_DIR)
    
    # Construir el comando para iniciar uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    print("La API estará disponible en: http://127.0.0.1:8000")
    print("Documentación de la API: http://127.0.0.1:8000/docs")
    
    # Ejecutar el comando
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"\nError al iniciar el servidor: {str(e)}")

if __name__ == "__main__":
    setup_env()
    start_server() 