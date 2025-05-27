import os
from dotenv import load_dotenv
from supabase import create_client, Client
from functools import lru_cache
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@lru_cache(maxsize=10)
def get_conexion() -> Client:
    """
    Crea y devuelve un cliente de Supabase para interactuar con la base de datos.
    Utiliza caché para optimizar el rendimiento en entornos sin servidor.
    
    Returns:
        Client: Cliente de Supabase inicializado.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Las variables de entorno SUPABASE_URL y SUPABASE_KEY deben estar configuradas. "
            "Por favor, verifica tu archivo .env o las variables de entorno en Vercel."
        )
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

