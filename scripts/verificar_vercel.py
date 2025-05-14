#!/usr/bin/env python
"""
Script para verificar que el proyecto esté listo para ser desplegado en Vercel.
"""
import os
import sys
import importlib.util
import subprocess
from pathlib import Path

def colored(text, color):
    """Retorna texto coloreado para la terminal."""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def check_file_exists(file_path, required=True):
    """Verifica si un archivo existe."""
    exists = os.path.exists(file_path)
    if exists:
        print(f"{colored('✓', 'green')} {file_path} encontrado")
    elif required:
        print(f"{colored('✗', 'red')} {file_path} no encontrado (requerido)")
    else:
        print(f"{colored('!', 'yellow')} {file_path} no encontrado (opcional)")
    return exists

def check_import(package):
    """Verifica si un paquete puede ser importado."""
    try:
        importlib.util.find_spec(package)
        print(f"{colored('✓', 'green')} Paquete {package} instalado")
        return True
    except ImportError:
        print(f"{colored('✗', 'red')} Paquete {package} no instalado")
        return False

def main():
    """Función principal para verificar la configuración."""
    print(colored("\n=== Verificando configuración para Vercel ===", "blue"))
    
    # Verificar archivos esenciales
    root_dir = Path(__file__).parent.parent
    files_to_check = [
        (root_dir / "vercel.json", True),
        (root_dir / "api" / "index.py", True),
        (root_dir / "requirements.txt", True),
        (root_dir / ".env", False)
    ]
    
    for file_path, required in files_to_check:
        check_file_exists(file_path, required)
    
    # Verificar paquetes necesarios
    packages = ["fastapi", "supabase", "dotenv", "pydantic"]
    all_packages_installed = all(check_import(pkg) for pkg in packages)
    
    # Verificar variables de entorno
    env_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"\n{colored('!', 'yellow')} Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("   Estas variables deben configurarse en Vercel para el despliegue.")
    else:
        print(f"\n{colored('✓', 'green')} Todas las variables de entorno necesarias están configuradas")
    
    # Verificar tamaño aproximado del proyecto (límite de Vercel: 50MB)
    try:
        # Obtener tamaño recursivo de la carpeta
        size_bytes = sum(f.stat().st_size for f in Path(root_dir).glob('**/*') if f.is_file())
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb < 40:
            print(f"{colored('✓', 'green')} Tamaño del proyecto: {size_mb:.2f}MB (dentro del límite de Vercel)")
        else:
            print(f"{colored('!', 'yellow')} Tamaño del proyecto: {size_mb:.2f}MB (cerca del límite de 50MB de Vercel)")
    except Exception as e:
        print(f"{colored('!', 'yellow')} No se pudo verificar el tamaño del proyecto: {e}")
    
    # Conclusión
    print("\n" + colored("=== Resultados ===", "blue"))
    if all_packages_installed and all(check_file_exists(f, r) for f, r in files_to_check if r):
        print(f"{colored('✓', 'green')} Tu proyecto parece estar listo para ser desplegado en Vercel!")
        print(f"\nPara desplegar, ejecuta: {colored('vercel', 'blue')} en la raíz del proyecto")
        print(f"o conecta tu repositorio directamente a Vercel para despliegue continuo.")
    else:
        print(f"{colored('✗', 'red')} Tu proyecto necesita algunos ajustes antes de poder desplegarlo en Vercel.")
        print("Por favor, soluciona los problemas indicados anteriormente.")

if __name__ == "__main__":
    main() 