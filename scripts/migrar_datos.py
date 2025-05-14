import os
import oracledb
from dotenv import load_dotenv
from supabase import create_client

def migrar_datos_oracle_a_supabase():
    """
    Script de ejemplo para migrar datos desde Oracle a Supabase.
    Requiere que ambos sistemas estén configurados correctamente.
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración de Oracle
    ORACLE_USER = os.getenv("ORACLE_USER")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
    ORACLE_DSN = os.getenv("ORACLE_DSN")
    
    # Configuración de Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    try:
        # Conectar a Oracle
        print("Conectando a Oracle...")
        conexion_oracle = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_DSN
        )
        cursor_oracle = conexion_oracle.cursor()
        
        # Conectar a Supabase
        print("Conectando a Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Consultar datos en Oracle
        print("Consultando datos en Oracle...")
        cursor_oracle.execute("SELECT rut, nombre, email FROM alumno")
        filas = cursor_oracle.fetchall()
        
        print(f"Se encontraron {len(filas)} registros para migrar")
        
        # Migrar datos a Supabase por lotes
        BATCH_SIZE = 100
        total_migrados = 0
        
        for i in range(0, len(filas), BATCH_SIZE):
            lote = filas[i:i+BATCH_SIZE]
            datos_supabase = []
            
            for rut, nombre, email in lote:
                datos_supabase.append({
                    "rut": rut,
                    "nombre": nombre,
                    "email": email
                })
            
            if datos_supabase:
                print(f"Migrando lote {i//BATCH_SIZE + 1}...")
                # Opción 1: Insertar ignorando duplicados (necesita que Supabase tenga configuración adecuada)
                response = supabase.table('alumno').upsert(datos_supabase).execute()
                
                # Verificar si hubo errores
                if hasattr(response, 'error') and response.error:
                    print(f"Error en lote {i//BATCH_SIZE + 1}: {response.error}")
                else:
                    total_migrados += len(datos_supabase)
                    print(f"Lote {i//BATCH_SIZE + 1} migrado correctamente")
        
        print(f"Migración completa. {total_migrados} registros migrados correctamente.")
        
    except Exception as ex:
        print(f"Error durante la migración: {str(ex)}")
    finally:
        # Cerrar conexiones
        if 'cursor_oracle' in locals():
            cursor_oracle.close()
        if 'conexion_oracle' in locals():
            conexion_oracle.close()
        
        print("Conexiones cerradas. Proceso finalizado.")

if __name__ == "__main__":
    migrar_datos_oracle_a_supabase() 