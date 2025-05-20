from fastapi import APIRouter, HTTPException, Body, Form
from app.database import get_conexion
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, constr, validator

# Modelo para la petición de login
class LoginRequest(BaseModel):
    correo: str
    contrasena: str

# Modelo para actualización de empleado
class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    rol_id: Optional[int] = None
    rut: Optional[str] = None
    contrasena: Optional[str] = None

# Modelo para crear empleado
class EmpleadoCreate(BaseModel):
    nombre: constr(min_length=2, max_length=50)
    apellido: constr(min_length=2, max_length=50)
    rut: constr(regex=r'^\d{7,8}-[\dkK]$')
    correo: EmailStr
    contrasena: constr(min_length=6)
    direccion: Optional[str] = "N/A"
    telefono: Optional[str] = "N/A"
    rol_id: int

    @validator('rol_id')
    def validar_rol(cls, v):
        if v not in [2, 3, 4, 5]:
            raise ValueError('Rol inválido. Debe ser 2 (Admin), 3 (Vendedor), 4 (Bodeguero) o 5 (Contador)')
        return v

    @validator('nombre', 'apellido')
    def validar_nombre_apellido(cls, v):
        if not v.strip():
            raise ValueError('No puede estar vacío')
        return v.strip()

    @validator('direccion', 'telefono')
    def validar_campos_opcionales(cls, v):
        if not v or not v.strip():
            return "N/A"
        return v.strip()

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
async def agregar_empleado(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    rol_id: int = Form(...),
    rut: str = Form(...),
    contrasena: str = Form(...)
):
    try:
        # Validaciones adicionales
        if not nombre or not apellido or not correo or not rut or not contrasena:
            raise HTTPException(status_code=422, detail="Todos los campos marcados son obligatorios")

        if rol_id not in [2, 3, 4, 5]:
            raise HTTPException(status_code=422, detail="Rol inválido. Debe ser 2 (Admin), 3 (Vendedor), 4 (Bodeguero) o 5 (Contador)")

        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si ya existe un empleado con el mismo correo
        check_email = supabase.table('empleado').select('*').eq('correo', correo).execute()
        if check_email.data and len(check_email.data) > 0:
            raise HTTPException(status_code=400, detail="Ya existe un empleado con este correo")

        # Verificar si ya existe un empleado con el mismo RUT
        check_rut = supabase.table('empleado').select('*').eq('rut', rut).execute()
        if check_rut.data and len(check_rut.data) > 0:
            raise HTTPException(status_code=400, detail="Ya existe un empleado con este RUT")

        # Preparar los datos para insertar
        datos_empleado = {
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "correo": correo.strip(),
            "telefono": telefono.strip() if telefono else "N/A",
            "direccion": direccion.strip() if direccion else "N/A",
            "rol_id": rol_id,
            "rut": rut.strip(),
            "contrasena": contrasena
        }
        
        # Insertar nuevo empleado
        response = supabase.table('empleado').insert(datos_empleado).execute()
        
        # Verificar si la inserción fue exitosa
        if response.data and len(response.data) > 0:
            empleado_creado = response.data[0]
            return {"mensaje": "Empleado agregado con éxito", "empleado": empleado_creado}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar empleado: No se recibieron datos de la base de datos")
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al agregar empleado: {str(ex)}")

@router.put("/{id_empleado}")
def actualizar_empleado(
    id_empleado: int,
    empleado: EmpleadoUpdate
):
    try:
        # Verificar que al menos un campo sea proporcionado
        datos_actualizar = {k: v for k, v in empleado.dict().items() if v is not None}
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar")
        
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el empleado existe
        check_response = supabase.table('empleado').select('id_empleado').eq('id_empleado', id_empleado).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
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