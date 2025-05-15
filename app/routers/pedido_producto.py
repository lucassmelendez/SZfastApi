from fastapi import APIRouter, HTTPException
from app.database import get_conexion
from typing import Optional, List
from pydantic import BaseModel

# Modelos para pedido_producto
class PedidoProductoBase(BaseModel):
    id_pedido: int
    id_producto: int
    cantidad: int
    precio_unitario: int
    subtotal: int

class PedidoProductoCreate(PedidoProductoBase):
    pass

class PedidoProductoUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None

# Modelo para lista de productos en un pedido
class ProductosEnPedido(BaseModel):
    productos: List[PedidoProductoCreate]

router = APIRouter(
    prefix="/pedido-producto",
    tags=["Pedido-Producto"]
)

@router.get("/pedido/{id_pedido}")
def obtener_productos_por_pedido(id_pedido: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_pedido = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_pedido.data or len(check_pedido.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Consultar productos del pedido
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/producto/{id_producto}")
def obtener_pedidos_por_producto(id_producto: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el producto existe
        check_producto = supabase.table('producto').select('id_producto').eq('id_producto', id_producto).execute()
        if not check_producto.data or len(check_producto.data) == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Consultar pedidos que contienen el producto
        response = supabase.table('pedido_producto').select('*').eq('id_producto', id_producto).execute()
        
        # Verificar si la respuesta contiene datos
        if not response.data:
            return []
        
        return response.data
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_producto_a_pedido(pedido_producto: PedidoProductoCreate):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        check_pedido = supabase.table('pedido').select('id_pedido').eq('id_pedido', pedido_producto.id_pedido).execute()
        if not check_pedido.data or len(check_pedido.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verificar si el producto existe
        check_producto = supabase.table('producto').select('id_producto').eq('id_producto', pedido_producto.id_producto).execute()
        if not check_producto.data or len(check_producto.data) == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar si el producto ya existe en el pedido
        check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', pedido_producto.id_pedido).eq('id_producto', pedido_producto.id_producto).execute()
        if check_existente.data and len(check_existente.data) > 0:
            raise HTTPException(status_code=400, detail="Este producto ya está en el pedido. Utilice PUT para actualizar.")
        
        # Insertar producto en el pedido
        response = supabase.table('pedido_producto').insert(pedido_producto.dict()).execute()
        
        # Verificar si la inserción fue exitosa
        if response.data:
            return {"mensaje": "Producto agregado al pedido con éxito", "pedido_producto": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar producto al pedido")
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/bulk/{id_pedido}")
def agregar_multiples_productos(id_pedido: int, productos: ProductosEnPedido):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si el pedido existe
        try:
            check_pedido = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
            if not check_pedido.data or len(check_pedido.data) == 0:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")
        except Exception as ex:
            print(f"Error al verificar existencia del pedido: {str(ex)}")
            # Continuamos el proceso aunque haya errores en la verificación
        
        # Preparar lista de productos para insertar
        productos_a_insertar = []
        for producto in productos.productos:
            # Asegurarse de que el id_pedido sea correcto
            if producto.id_pedido != id_pedido:
                producto_dict = producto.dict()
                producto_dict['id_pedido'] = id_pedido
                productos_a_insertar.append(producto_dict)
            else:
                productos_a_insertar.append(producto.dict())
        
        print(f"Intentando insertar {len(productos_a_insertar)} productos en el pedido {id_pedido}")
        print(f"Primer producto: {productos_a_insertar[0] if productos_a_insertar else 'No hay productos'}")
        
        # Insertar múltiples productos en el pedido
        try:
            response = supabase.table('pedido_producto').insert(productos_a_insertar).execute()
            
            # Verificar si la inserción fue exitosa
            if response.data:
                return {"mensaje": f"Se agregaron {len(response.data)} productos al pedido con éxito", "productos": response.data}
            else:
                print("No se obtuvieron datos en la respuesta de inserción de productos")
                raise HTTPException(status_code=500, detail="Error al agregar productos al pedido: No se recibieron datos de respuesta")
        except Exception as insert_ex:
            print(f"Error específico al insertar productos: {str(insert_ex)}")
            raise HTTPException(status_code=500, detail=f"Error al insertar productos: {str(insert_ex)}")
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        print(f"Error general al agregar productos al pedido: {str(ex)}")
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{id_pedido}/{id_producto}")
def actualizar_producto_en_pedido(id_pedido: int, id_producto: int, datos: PedidoProductoUpdate):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si la relación pedido-producto existe
        check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        # Crear diccionario con campos a actualizar (excluyendo los None)
        datos_actualizar = {k: v for k, v in datos.dict().items() if v is not None}
        
        # Si no hay datos para actualizar, retornar
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Actualizar producto en pedido
        response = supabase.table('pedido_producto').update(datos_actualizar).eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        return {"mensaje": "Producto en pedido actualizado con éxito", "pedido_producto": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_pedido}/{id_producto}")
def eliminar_producto_de_pedido(id_pedido: int, id_producto: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Verificar si la relación pedido-producto existe
        check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        # Eliminar producto del pedido
        response = supabase.table('pedido_producto').delete().eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        return {"mensaje": "Producto eliminado del pedido con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_pedido_producto}")
def obtener_detalle_pedido_producto(id_pedido_producto: int):
    try:
        # Obtener conexión a Supabase
        supabase = get_conexion()
        
        # Consultar detalle pedido_producto por id
        response = supabase.table('pedido_producto').select('*').eq('id_pedido_producto', id_pedido_producto).execute()
        
        # Verificar si se encontró el detalle
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Detalle de pedido-producto no encontrado")
        
        # Obtener el detalle (debería ser único por id)
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex)) 