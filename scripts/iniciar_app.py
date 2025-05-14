import subprocess
import os
import sys

def iniciar_app():
    """
    Inicia la aplicación FastAPI usando uvicorn.
    """
    print("Iniciando la API con FastAPI y Supabase...")
    
    # Obtener la ruta raíz del proyecto (subiendo dos niveles desde este script)
    ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Verificar que el archivo .env existe
    ruta_env = os.path.join(ruta_raiz, '.env')
    if not os.path.exists(ruta_env):
        print("ADVERTENCIA: No se encontró el archivo .env")
        print("Por favor, crea este archivo con las variables SUPABASE_URL y SUPABASE_KEY")
        print("Ejemplo:")
        print("SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("SUPABASE_KEY=tu-api-key-de-supabase")
        respuesta = input("¿Deseas continuar de todos modos? (s/n): ")
        if respuesta.lower() != 's':
            sys.exit(1)
    
    # Determinar el host y puerto
    host = '127.0.0.1'
    puerto = 8000
    
    # Construir el comando para iniciar la aplicación
    comando = [
        'uvicorn',
        'app.main:app',
        '--host', host,
        '--port', str(puerto),
        '--reload'
    ]
    
    # Iniciar el servidor
    print(f"La API estará disponible en http://{host}:{puerto}")
    print("Swagger UI: http://127.0.0.1:8000/docs")
    print("ReDoc: http://127.0.0.1:8000/redoc")
    print("\nPresiona Ctrl+C para detener el servidor")
    
    try:
        subprocess.run(comando, cwd=ruta_raiz)
    except KeyboardInterrupt:
        print("\nServidor detenido")

if __name__ == "__main__":
    iniciar_app() 