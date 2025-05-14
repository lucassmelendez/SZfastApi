#!/usr/bin/env python
"""
Script para verificar y configurar las variables de entorno necesarias para la API.
Este script configura temporalmente las variables para la sesión actual.
"""
import os
import sys

def setup_env():
    """Configura las variables de entorno para la API."""
    print("Configurando variables de entorno para la API...")
    
    # Verificar si ya existen variables de entorno
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        print("Las variables de entorno ya están configuradas:")
        print(f"SUPABASE_URL: {supabase_url}")
        print(f"SUPABASE_KEY: {'*' * len(supabase_key)}")  # Ocultar la clave por seguridad
        return
    
    # Solicitar las variables si no existen
    print("No se encontraron las variables de entorno necesarias.")
    
    # Para desarrollo, usar valores de ejemplo
    os.environ["SUPABASE_URL"] = "https://ejemplo.supabase.co"
    os.environ["SUPABASE_KEY"] = "ejemplo-api-key"
    
    print("\nVariables de entorno configuradas temporalmente para desarrollo:")
    print("SUPABASE_URL: https://ejemplo.supabase.co")
    print("SUPABASE_KEY: ejemplo-api-key")
    print("\nNOTA: Estas son variables temporales solo para esta sesión.")
    print("      Para uso en producción, debes crear un archivo .env con tus credenciales reales.")

if __name__ == "__main__":
    setup_env() 