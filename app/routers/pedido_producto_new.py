from fastapi import APIRouter, HTTPException
from app.database import get_conexion
from typing import Optional, List, Tuple
from pydantic import BaseModel

def calcular_descuento_producto(cantidad: int, precio_unitario: int, aplicar_descuento: bool = False) -> Tuple[int, int]:
    """Calcula el descuento y subtotal para un producto.
    
    Args:
        cantidad: Cantidad del producto
        precio_unitario: Precio por unidad
        aplicar_descuento: Si se debe aplicar el descuento del 5%
        
    Returns:
        tuple[int, int]: (subtotal_final, descuento)
    """
    subtotal_original = cantidad * precio_unitario
    descuento = int(subtotal_original * 0.05) if aplicar_descuento else 0
    subtotal_final = subtotal_original - descuento
    return (subtotal_final, descuento)

class PedidoProductoBase(BaseModel):
    cantidad: int
    precio_unitario: int
    subtotal: int
    descuento: Optional[int] = 0
    id_pedido: int
    id_producto: int

class PedidoProductoCreate(PedidoProductoBase):
    pass

class PedidoProductoUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None

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
        
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        if not response.data:
            return []
        
        # Calculate total quantity to see if discount should apply
        total_cantidad = sum(item['cantidad'] for item in response.data)
        aplicar_descuento = total_cantidad > 4
        
        # Update discount values if needed
        for producto in response.data:
            subtotal_original = producto['cantidad'] * producto['precio_unitario']
            if aplicar_descuento:
                producto['descuento'] = int(subtotal_original * 0.05)
                producto['subtotal'] = subtotal_original - producto['descuento']
        
        return response.data
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_producto_a_pedido(pedido_producto: PedidoProductoCreate):
    try:
        supabase = get_conexion()
        
        # First get total products in order to check if discount applies
        existing_products = supabase.table('pedido_producto').select('*').eq('id_pedido', pedido_producto.id_pedido).execute()
        total_cantidad = sum(item['cantidad'] for item in existing_products.data) + pedido_producto.cantidad
        aplicar_descuento = total_cantidad > 4
        
        # Calculate discount
        subtotal_final, descuento = calcular_descuento_producto(
            pedido_producto.cantidad,
            pedido_producto.precio_unitario,
            aplicar_descuento
        )
        
        datos_producto = {
            "cantidad": pedido_producto.cantidad,
            "precio_unitario": pedido_producto.precio_unitario,
            "subtotal": subtotal_final,
            "descuento": descuento,
            "id_pedido": pedido_producto.id_pedido,
            "id_producto": pedido_producto.id_producto
        }
        
        response = supabase.table('pedido_producto').insert(datos_producto).execute()
        
        if response.data and len(response.data) > 0:
            # If successful, recalculate all discounts in the order
            recalcular_descuentos_pedido(pedido_producto.id_pedido)
            return response.data[0]
        else:
            print("No se recibieron datos en la respuesta de inserción de producto")
            return datos_producto
            
    except Exception as ex:
        print(f"Error al agregar producto a pedido: {str(ex)}")
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/bulk/{id_pedido}")
async def agregar_multiples_productos(id_pedido: int, productos: ProductosEnPedido):
    try:
        supabase = get_conexion()
        
        # Calculate total quantity for discount
        total_cantidad = sum(p.cantidad for p in productos.productos)
        aplicar_descuento = total_cantidad > 4
        
        # Prepare products with discount calculation
        productos_a_insertar = []
        for producto in productos.productos:
            subtotal_final, descuento = calcular_descuento_producto(
                producto.cantidad,
                producto.precio_unitario,
                aplicar_descuento
            )
            
            producto_dict = {
                "cantidad": producto.cantidad,
                "precio_unitario": producto.precio_unitario,
                "subtotal": subtotal_final,
                "descuento": descuento,
                "id_pedido": id_pedido,
                "id_producto": producto.id_producto
            }
            productos_a_insertar.append(producto_dict)
        
        try:
            response = supabase.table('pedido_producto').insert(productos_a_insertar).execute()
            
            if response.data:
                return {
                    "mensaje": f"Se agregaron {len(response.data)} productos al pedido con éxito",
                    "productos": response.data,
                    "aplicar_descuento": aplicar_descuento,
                    "total_productos": total_cantidad
                }
            else:
                raise HTTPException(status_code=500, detail="Error al agregar productos al pedido")
        except Exception as insert_ex:
            print(f"Error al insertar productos: {str(insert_ex)}")
            raise HTTPException(status_code=500, detail=str(insert_ex))
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/pedido/{id_pedido}/recalcular-descuentos")
async def recalcular_descuentos_pedido(id_pedido: int):
    try:
        supabase = get_conexion()
        
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontraron productos en el pedido")
        
        total_cantidad = sum(item['cantidad'] for item in response.data)
        aplicar_descuento = total_cantidad > 4
        
        # Update each product's discount and subtotal
        for producto in response.data:
            subtotal_final, descuento = calcular_descuento_producto(
                producto['cantidad'],
                producto['precio_unitario'],
                aplicar_descuento
            )
            
            supabase.table('pedido_producto').update({
                'descuento': descuento,
                'subtotal': subtotal_final
            }).eq('id_pedido', id_pedido).eq('id_producto', producto['id_producto']).execute()
        
        # Get updated products
        updated_response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        return {
            "mensaje": "Descuentos recalculados con éxito",
            "aplicar_descuento": aplicar_descuento,
            "total_productos": total_cantidad,
            "productos": updated_response.data
        }
        
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{id_pedido}/{id_producto}")
async def actualizar_producto_en_pedido(id_pedido: int, id_producto: int, datos: PedidoProductoUpdate):
    try:
        supabase = get_conexion()
        
        check_existente = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        # If quantity or price is being updated, recalculate discount
        if 'cantidad' in datos or 'precio_unitario' in datos:
            producto_actual = check_existente.data[0]
            nueva_cantidad = datos.cantidad or producto_actual['cantidad']
            nuevo_precio = datos.precio_unitario or producto_actual['precio_unitario']
            
            # Get total products to check if discount applies
            total_response = supabase.table('pedido_producto').select('cantidad').eq('id_pedido', id_pedido).execute()
            total_cantidad = sum(item['cantidad'] for item in total_response.data if item['id_producto'] != id_producto) + nueva_cantidad
            aplicar_descuento = total_cantidad > 4
            
            subtotal_final, descuento = calcular_descuento_producto(nueva_cantidad, nuevo_precio, aplicar_descuento)
            datos.subtotal = subtotal_final
            datos.descuento = descuento
        
        datos_actualizar = {k: v for k, v in datos.dict().items() if v is not None}
        
        response = supabase.table('pedido_producto').update(datos_actualizar).eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        # After update, recalculate all discounts in the order
        await recalcular_descuentos_pedido(id_pedido)
        
        return {"mensaje": "Producto en pedido actualizado con éxito", "pedido_producto": response.data[0]}
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_pedido}/{id_producto}")
async def eliminar_producto_de_pedido(id_pedido: int, id_producto: int):
    try:
        supabase = get_conexion()
        
        check_existente = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        response = supabase.table('pedido_producto').delete().eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        # After deletion, recalculate discounts for remaining products
        await recalcular_descuentos_pedido(id_pedido)
        
        return {"mensaje": "Producto eliminado del pedido con éxito"}
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