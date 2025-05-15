from fastapi import APIRouter, HTTPException, Body
from app.database import get_conexion
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

# Modelo para pedido
class PedidoBase(BaseModel):
    fecha: Optional[datetime] = None
    medio_pago_id: int
    id_estado_envio: int
    id_estado: int
    id_cliente: int

class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    fecha: Optional[datetime] = None
    medio_pago_id: Optional[int] = None
    id_estado_envio: Optional[int] = None
    id_estado: Optional[int] = None
    id_cliente: Optional[int] = None

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

# Endpoints: GET, GET, POST, PUT, DELETE, PATCH
@router.get("/")
def obtener_pedidos():
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar todos los pedidos de la tabla 'pedido'
        response = supabase.table('pedido').select('*').execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_pedido}")
def obtener_pedido(id_pedido: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar pedido por id
        response = supabase.table('pedido').select('*').eq('id_pedido', id_pedido).execute()
        
        # Verificar si se encontró el pedido
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Obtener el primer pedido (debería ser único por id)
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def crear_pedido(pedido: PedidoCreate):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Preparar los datos del pedido
        datos_pedido = pedido.dict()
        
        # Si no se proporciona una fecha, usar la fecha actual
        if not datos_pedido.get("fecha"):
            datos_pedido["fecha"] = datetime.now().isoformat()
        
        # Insertar nuevo pedido
        response = supabase.table('pedido').insert(datos_pedido).execute()
        
        # Verificar si la inserción fue exitosa
        if response.data:
            return {"mensaje": "Pedido creado con éxito", "pedido": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Error al crear pedido")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{id_pedido}")
def actualizar_pedido(id_pedido: int, pedido: PedidoUpdate):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_response = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Crear diccionario con campos a actualizar (excluyendo los None)
        datos_actualizar = {k: v for k, v in pedido.dict().items() if v is not None}
        
        # Si no hay datos para actualizar, retornar
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Actualizar pedido
        response = supabase.table('pedido').update(datos_actualizar).eq('id_pedido', id_pedido).execute()
        
        return {"mensaje": "Pedido actualizado con éxito", "pedido": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_pedido}")
def eliminar_pedido(id_pedido: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_response = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Eliminar pedido
        response = supabase.table('pedido').delete().eq('id_pedido', id_pedido).execute()
        
        return {"mensaje": "Pedido eliminado con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/cliente/{id_cliente}")
def obtener_pedidos_por_cliente(id_cliente: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar pedidos por id_cliente
        response = supabase.table('pedido').select('*').eq('id_cliente', id_cliente).execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.patch("/{id_pedido}/estado")
def actualizar_estado_pedido(id_pedido: int, id_estado: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_response = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Actualizar solo el estado del pedido
        response = supabase.table('pedido').update({"id_estado": id_estado}).eq('id_pedido', id_pedido).execute()
        
        return {"mensaje": "Estado del pedido actualizado con éxito", "pedido": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.patch("/{id_pedido}/estado-envio")
def actualizar_estado_envio(id_pedido: int, id_estado_envio: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_response = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Actualizar solo el estado de envío del pedido
        response = supabase.table('pedido').update({"id_estado_envio": id_estado_envio}).eq('id_pedido', id_pedido).execute()
        
        return {"mensaje": "Estado de envío actualizado con éxito", "pedido": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex)) 