from fastapi import APIRouter, HTTPException, Body
from app.database import get_conexion
from typing import Optional, Dict
from pydantic import BaseModel

# Modelo para la petición de login
class LoginRequest(BaseModel):
    correo: str
    contrasena: str

# Modelo para actualización de cliente
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    id_rol: Optional[int] = None
    rut: Optional[str] = None
    contrasena: Optional[str] = None

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# Endpoints: GET, GET, POST, PUT, DELETE, PATCH
@router.get("/")
def obtener_clientes():
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar todos los clientes de la tabla 'cliente'
        response = supabase.table('cliente').select('*').execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_cliente}")
def obtener_cliente(id_cliente: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar cliente por id
        response = supabase.table('cliente').select('*').eq('id_cliente', id_cliente).execute()
        
        # Verificar si se encontró el cliente
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener el primer cliente (debería ser único por id)
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_cliente(
    nombre: str, 
    apellido: str, 
    correo: str, 
    telefono: str, 
    direccion: str, 
    id_rol: int, 
    rut: str, 
    contrasena: str
):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Insertar nuevo cliente
        response = supabase.table('cliente').insert({
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "telefono": telefono,
            "direccion": direccion,
            "id_rol": id_rol,
            "rut": rut,
            "contrasena": contrasena
        }).execute()
        
        # Verificar si la inserción fue exitosa
        if response.data:
            return {"mensaje": "Cliente agregado con éxito", "cliente": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar cliente")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{id_cliente}")
def actualizar_cliente(
    id_cliente: int,
    cliente: ClienteUpdate
):
    try:
        # Verificar que al menos un campo sea proporcionado
        datos_actualizar = {k: v for k, v in cliente.dict().items() if v is not None}
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar")
        
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el cliente existe
        check_response = supabase.table('cliente').select('id_cliente').eq('id_cliente', id_cliente).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Actualizar cliente
        response = supabase.table('cliente').update(datos_actualizar).eq('id_cliente', id_cliente).execute()
        
        return {"mensaje": "Cliente actualizado con éxito", "cliente": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_cliente}")
def eliminar_cliente(id_cliente: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el cliente existe
        check_response = supabase.table('cliente').select('id_cliente').eq('id_cliente', id_cliente).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Eliminar cliente
        response = supabase.table('cliente').delete().eq('id_cliente', id_cliente).execute()
        
        return {"mensaje": "Cliente eliminado con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/rut/{rut}")
def obtener_cliente_por_rut(rut: str):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar cliente por rut
        response = supabase.table('cliente').select('*').eq('rut', rut).execute()
        
        # Verificar si se encontró el cliente
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener el primer cliente con ese rut
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/login", status_code=200)
def login_cliente(login_data: LoginRequest):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Buscar cliente por correo
        response = supabase.table('cliente').select('*').eq('correo', login_data.correo).execute()
        
        # Verificar si se encontró el cliente
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener el cliente
        cliente = response.data[0]
        
        # Verificar contraseña
        if cliente['contrasena'] != login_data.contrasena:
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Eliminar contraseña del objeto de respuesta por seguridad
        del cliente['contrasena']
        
        return {"mensaje": "Inicio de sesión exitoso", "cliente": cliente}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex)) 