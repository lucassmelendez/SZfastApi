import logging

# Configurar el nivel de logging para diferentes loggers
def configure_logging():
    # Configurar el logger de httpx
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)  # Cambia a WARNING para eliminar los mensajes INFO
    
    # También puedes configurar otros loggers si es necesario
    # fastapi_logger = logging.getLogger("fastapi")
    # fastapi_logger.setLevel(logging.INFO)
    
    # Configuración del formato de logs (opcional)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    
    # Añadir el handler a los loggers
    httpx_logger.addHandler(handler) 