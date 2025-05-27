from fastapi import APIRouter, HTTPException
from app.database import get_conexion
from typing import Optional, List
from pydantic import BaseModel

class PedidoProductoBase(BaseModel):
    cantidad: int
    precio_unitario: int
    subtotal: int
    id_pedido: int
    id_producto: int

class PedidoProductoCreate(PedidoProductoBase):
    pass

class PedidoProductoUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None

class ProductosEnPedido(BaseModel):
    productos: List[PedidoProductoCreate]

router = APIRouter(
    prefix="/pedido-producto",
    tags=["Pedido-Producto"]
)

@router.get("/pedido/{id_pedido}")
def obtener_productos_por_pedido(id_pedido: int):
    try:
        supabase = get_conexion()
        
        check_pedido = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_pedido.data or len(check_pedido.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
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
        supabase = get_conexion()
        
        check_producto = supabase.table('producto').select('id_producto').eq('id_producto', id_producto).execute()
        if not check_producto.data or len(check_producto.data) == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        response = supabase.table('pedido_producto').select('*').eq('id_producto', id_producto).execute()
        
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
        supabase = get_conexion()
        
        datos_producto = {
            "cantidad": pedido_producto.cantidad,
            "precio_unitario": pedido_producto.precio_unitario,
            "subtotal": pedido_producto.subtotal,
            "id_pedido": pedido_producto.id_pedido,
            "id_producto": pedido_producto.id_producto
        }
        
        print(f"Intentando insertar producto {datos_producto['id_producto']} en pedido {datos_producto['id_pedido']}")
        
        try:
            check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', datos_producto['id_pedido']).eq('id_producto', datos_producto['id_producto']).execute()
            
            if check_existente.data and len(check_existente.data) > 0:
                print(f"Producto ya existe en el pedido. Actualizando cantidad.")
                
                response = supabase.table('pedido_producto').update({
                    "cantidad": datos_producto['cantidad'],
                    "precio_unitario": datos_producto['precio_unitario'],
                    "subtotal": datos_producto['subtotal']
                }).eq('id_pedido', datos_producto['id_pedido']).eq('id_producto', datos_producto['id_producto']).execute()
                
                return {"mensaje": "Producto actualizado en el pedido", "pedido_producto": response.data[0] if response.data else None}
        except Exception as check_ex:
            print(f"Error al verificar existencia del producto: {str(check_ex)}. Continuando con inserción.")
        
        response = supabase.table('pedido_producto').insert(datos_producto).execute()
        
        if response.data and len(response.data) > 0:
            try:
                pedido_response = supabase.table('pedido').select('medio_pago_id').eq('id_pedido', datos_producto['id_pedido']).execute()
                
                if pedido_response.data and len(pedido_response.data) > 0 and pedido_response.data[0]['medio_pago_id'] == 1:
                    try:
                        producto_response = supabase.table('producto').select('stock').eq('id_producto', datos_producto['id_producto']).execute()
                        
                        if producto_response.data and len(producto_response.data) > 0:
                            producto = producto_response.data[0]
                            
                            nuevo_stock = max(0, producto['stock'] - datos_producto['cantidad'])
                            
                            update_response = supabase.table('producto').update({'stock': nuevo_stock}).eq('id_producto', datos_producto['id_producto']).execute()
                            
                            if update_response.error:
                                print(f"Error al actualizar stock del producto {datos_producto['id_producto']}: {update_response.error}")
                            else:
                                print(f"Stock actualizado para producto {datos_producto['id_producto']}: {producto['stock']} -> {nuevo_stock}")
                    except Exception as stock_ex:
                        print(f"Error al actualizar stock del producto: {str(stock_ex)}")
            except Exception as pedido_ex:
                print(f"Error al verificar el tipo de pago del pedido: {str(pedido_ex)}")
            
            return response.data[0]
        else:
            print("No se recibieron datos en la respuesta de inserción de producto")
            return datos_producto
            
    except Exception as ex:
        print(f"Error al agregar producto a pedido: {str(ex)}")
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/bulk/{id_pedido}")
def agregar_multiples_productos(id_pedido: int, productos: ProductosEnPedido):
    try:
        supabase = get_conexion()
        
        try:
            check_pedido = supabase.table('pedido').select('id_pedido, medio_pago_id').eq('id_pedido', id_pedido).execute()
            if not check_pedido.data or len(check_pedido.data) == 0:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
            pedido = check_pedido.data[0]
            es_transferencia = pedido['medio_pago_id'] == 1
        except Exception as ex:
            print(f"Error al verificar existencia del pedido: {str(ex)}")
            es_transferencia = False
        
        productos_a_insertar = []
        for producto in productos.productos:
            if producto.id_pedido != id_pedido:
                producto_dict = {
                    "cantidad": producto.cantidad,
                    "precio_unitario": producto.precio_unitario,
                    "subtotal": producto.subtotal,
                    "id_pedido": id_pedido,
                    "id_producto": producto.id_producto
                }
                productos_a_insertar.append(producto_dict)
            else:
                producto_dict = {
                    "cantidad": producto.cantidad,
                    "precio_unitario": producto.precio_unitario,
                    "subtotal": producto.subtotal,
                    "id_pedido": producto.id_pedido,
                    "id_producto": producto.id_producto
                }
                productos_a_insertar.append(producto_dict)
        
        print(f"Intentando insertar {len(productos_a_insertar)} productos en el pedido {id_pedido}")
        print(f"Primer producto: {productos_a_insertar[0] if productos_a_insertar else 'No hay productos'}")
        
        try:
            response = supabase.table('pedido_producto').insert(productos_a_insertar).execute()
            
            if response.data:
                if es_transferencia:
                    print(f"Actualizando stock para {len(productos_a_insertar)} productos (pago por transferencia)")
                    for producto in productos_a_insertar:
                        try:
                            producto_response = supabase.table('producto').select('stock').eq('id_producto', producto['id_producto']).execute()
                            
                            if producto_response.data and len(producto_response.data) > 0:
                                stock_actual = producto_response.data[0]['stock']
                                
                                nuevo_stock = max(0, stock_actual - producto['cantidad'])
                                
                                update_response = supabase.table('producto').update({'stock': nuevo_stock}).eq('id_producto', producto['id_producto']).execute()
                                
                                if update_response.error:
                                    print(f"Error al actualizar stock del producto {producto['id_producto']}: {update_response.error}")
                                else:
                                    print(f"Stock actualizado para producto {producto['id_producto']}: {stock_actual} -> {nuevo_stock}")
                        except Exception as stock_ex:
                            print(f"Error al actualizar stock del producto {producto['id_producto']}: {str(stock_ex)}")
                
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
        supabase = get_conexion()
        
        check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        datos_actualizar = {k: v for k, v in datos.dict().items() if v is not None}
        
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        response = supabase.table('pedido_producto').update(datos_actualizar).eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        return {"mensaje": "Producto en pedido actualizado con éxito", "pedido_producto": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_pedido}/{id_producto}")
def eliminar_producto_de_pedido(id_pedido: int, id_producto: int):
    try:
        supabase = get_conexion()
        
        check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        response = supabase.table('pedido_producto').delete().eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        return {"mensaje": "Producto eliminado del pedido con éxito"}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{id_pedido_producto}")
def obtener_detalle_pedido_producto(id_pedido_producto: int):
    try:
        supabase = get_conexion()
        
        response = supabase.table('pedido_producto').select('*').eq('id_pedido_producto', id_pedido_producto).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Detalle de pedido-producto no encontrado")
        
        return response.data[0]
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/productos/mas-vendidos")
def obtener_productos_mas_vendidos(limit: Optional[int] = 15):
    try:
        supabase = get_conexion()
        
        pedido_productos = supabase.table('pedido_producto').select('id_producto, cantidad').execute()
        
        if not pedido_productos.data:
            return []
        
        ventas_por_producto = {}
        for item in pedido_productos.data:
            id_producto = item['id_producto']
            cantidad = item['cantidad']
            
            if id_producto in ventas_por_producto:
                ventas_por_producto[id_producto] += cantidad
            else:
                ventas_por_producto[id_producto] = cantidad
        
        productos_ordenados = sorted(
            ventas_por_producto.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        if limit > 0:
            productos_ordenados = productos_ordenados[:limit]
        
        ids_productos = [producto[0] for producto in productos_ordenados]
        
        if not ids_productos:
            return []
        
        productos = []
        for id_producto, total_vendido in productos_ordenados:
            producto_info = supabase.table('producto').select('*').eq('id_producto', id_producto).execute()
            
            if producto_info.data and len(producto_info.data) > 0:
                producto = producto_info.data[0]
                producto['total_vendido'] = total_vendido
                productos.append(producto)
        
        return productos
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=f"Error al obtener productos más vendidos: {str(ex)}") 