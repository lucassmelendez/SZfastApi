from fastapi import APIRouter, HTTPException, Body
from app.database import get_conexion
from typing import Optional, Dict
from pydantic import BaseModel

# Modelo para la petición de login
class LoginRequest(BaseModel):
    correo: str
    contrasena: str

router = APIRouter(
    prefix="/empleados",
    tags=["Empleados"]
)

# Endpoints: GET, GET, POST, PUT, DELETE, PATCH
@router.get("/")
def obtener_empleados():
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar todos los empleados de la tabla 'empleado'
        response = supabase.table('empleado').select('*').execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_empleado}")
def obtener_empleado(id_empleado: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar empleado por id
        response = supabase.table('empleado').select('*').eq('id_empleado', id_empleado).execute()
        
        # Verificar si se encontró el empleado
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Obtener el primer empleado (debería ser único por id)
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_empleado(
    nombre: str, 
    apellido: str, 
    rut: str, 
    correo: str, 
    contrasena: str, 
    direccion: str, 
    telefono: str, 
    rol_id: int, 
    informe_id: int
):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Insertar nuevo empleado
        response = supabase.table('empleado').insert({
            "nombre": nombre,
            "apellido": apellido,
            "rut": rut,
            "correo": correo,
            "contrasena": contrasena,
            "direccion": direccion,
            "telefono": telefono,
            "rol_id": rol_id,
            "informe_id": informe_id
        }).execute()
        
        # Verificar si la inserción fue exitosa
        if response.data:
            return {"mensaje": "Empleado agregado con éxito", "empleado": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar empleado")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{id_empleado}")
def actualizar_empleado(
    id_empleado: int,
    nombre: Optional[str] = None,
    apellido: Optional[str] = None,
    rut: Optional[str] = None,
    correo: Optional[str] = None,
    contrasena: Optional[str] = None,
    direccion: Optional[str] = None,
    telefono: Optional[str] = None,
    rol_id: Optional[int] = None,
    informe_id: Optional[int] = None
):
    try:
        # Verificar que al menos un campo sea proporcionado
        if not any([nombre, apellido, rut, correo, contrasena, direccion, telefono, rol_id, informe_id]):
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar")
        
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el empleado existe
        check_response = supabase.table('empleado').select('id_empleado').eq('id_empleado', id_empleado).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Crear diccionario con campos a actualizar
        datos_actualizar = {}
        if nombre is not None:
            datos_actualizar["nombre"] = nombre
        if apellido is not None:
            datos_actualizar["apellido"] = apellido
        if rut is not None:
            datos_actualizar["rut"] = rut
        if correo is not None:
            datos_actualizar["correo"] = correo
        if contrasena is not None:
            datos_actualizar["contrasena"] = contrasena
        if direccion is not None:
            datos_actualizar["direccion"] = direccion
        if telefono is not None:
            datos_actualizar["telefono"] = telefono
        if rol_id is not None:
            datos_actualizar["rol_id"] = rol_id
        if informe_id is not None:
            datos_actualizar["informe_id"] = informe_id
        
        # Actualizar empleado
        response = supabase.table('empleado').update(datos_actualizar).eq('id_empleado', id_empleado).execute()
        
        return {"mensaje": "Empleado actualizado con éxito", "empleado": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_empleado}")
def eliminar_empleado(id_empleado: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el empleado existe
        check_response = supabase.table('empleado').select('id_empleado').eq('id_empleado', id_empleado).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Eliminar empleado
        response = supabase.table('empleado').delete().eq('id_empleado', id_empleado).execute()
        
        return {"mensaje": "Empleado eliminado con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/rut/{rut}")
def obtener_empleado_por_rut(rut: str):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar empleado por rut
        response = supabase.table('empleado').select('*').eq('rut', rut).execute()
        
        # Verificar si se encontró el empleado
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Obtener el primer empleado con ese rut
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/login", status_code=200)
def login_empleado(login_data: LoginRequest):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Buscar empleado por correo y contraseña
        response = supabase.table('empleado').select('*').eq('correo', login_data.correo).execute()
        
        # Verificar si se encontró el empleado
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Obtener el empleado
        empleado = response.data[0]
        
        # Verificar contraseña
        if empleado['contrasena'] != login_data.contrasena:
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Eliminar contraseña del objeto de respuesta por seguridad
        del empleado['contrasena']
        
        return {"mensaje": "Inicio de sesión exitoso", "empleado": empleado}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex)) 