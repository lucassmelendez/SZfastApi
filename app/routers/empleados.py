from fastapi import APIRouter, HTTPException, Body
from app.database import get_conexion
from typing import Optional, Dict
from pydantic import BaseModel

class LoginRequest(BaseModel):
    correo: str
    contrasena: str

class EmpleadoCreate(BaseModel):
    nombre: str
    apellido: str
    rut: str
    correo: str
    contrasena: str
    direccion: str
    telefono: str
    rol_id: int

def format_rut(rut: str) -> str:
    rut = rut.strip().replace(" ", "").replace(".", "")
    
    if "-" not in rut and len(rut) >= 2:
        rut = rut[:-1] + "-" + rut[-1]
    
    return rut

router = APIRouter(
    prefix="/empleados",
    tags=["Empleados"]
)

@router.get("/")
def obtener_empleados():
    try:
        supabase = get_conexion()
        
        response = supabase.table('empleado').select('*').execute()
        
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_empleado}")
def obtener_empleado(id_empleado: int):
    try:
        supabase = get_conexion()
        
        response = supabase.table('empleado').select('*').eq('id_empleado', id_empleado).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_empleado(empleado: EmpleadoCreate):
    try:
        rut_formateado = format_rut(empleado.rut)
        
        supabase = get_conexion()
        
        check_rut = supabase.table('empleado').select('id_empleado').eq('rut', rut_formateado).execute()
        if check_rut.data and len(check_rut.data) > 0:
            raise HTTPException(status_code=409, detail=f"Ya existe un empleado con el RUT: {rut_formateado}")
        
        response = supabase.table('empleado').insert({
            "nombre": empleado.nombre,
            "apellido": empleado.apellido,
            "rut": rut_formateado,
            "correo": empleado.correo,
            "contrasena": empleado.contrasena,
            "direccion": empleado.direccion,
            "telefono": empleado.telefono,
            "rol_id": empleado.rol_id
        }).execute()
        
        if response.data:
            return {"mensaje": "Empleado agregado con éxito", "empleado": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar empleado")
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=f"Error al crear empleado: {str(ex)}")

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
    rol_id: Optional[int] = None
):
    try:
        if not any([nombre, apellido, rut, correo, contrasena, direccion, telefono, rol_id]):
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar")
        
        supabase = get_conexion()
        
        check_response = supabase.table('empleado').select('id_empleado').eq('id_empleado', id_empleado).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
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
        
        response = supabase.table('empleado').update(datos_actualizar).eq('id_empleado', id_empleado).execute()
        
        return {"mensaje": "Empleado actualizado con éxito", "empleado": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_empleado}")
def eliminar_empleado(id_empleado: int):
    try:
        supabase = get_conexion()
        
        check_response = supabase.table('empleado').select('id_empleado').eq('id_empleado', id_empleado).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        response = supabase.table('empleado').delete().eq('id_empleado', id_empleado).execute()
        
        return {"mensaje": "Empleado eliminado con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/rut/{rut}")
def obtener_empleado_por_rut(rut: str):
    try:
        supabase = get_conexion()
        
        response = supabase.table('empleado').select('*').eq('rut', rut).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/login", status_code=200)
def login_empleado(login_data: LoginRequest):
    try:
        supabase = get_conexion()
        
        response = supabase.table('empleado').select('*').eq('correo', login_data.correo).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        empleado = response.data[0]
        
        if empleado['contrasena'] != login_data.contrasena:
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        del empleado['contrasena']
        
        return {"mensaje": "Inicio de sesión exitoso", "empleado": empleado}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex)) 