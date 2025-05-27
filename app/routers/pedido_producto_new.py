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
        
        check_pedido = supabase.table('pedido').select('id_pedido').eq('id_pedido', id_pedido).execute()
        if not check_pedido.data or len(check_pedido.data) == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Get all products with their discount information
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        if not response.data:
            return {
                "productos": [],
                "resumen": {
                    "total_productos": 0,
                    "aplicar_descuento": False,
                    "total_original": 0,
                    "total_descuentos": 0,
                    "total_final": 0,
                    "porcentaje_descuento": "0%"
                }
            }
        
        # Calculate total quantity and decide if discount applies
        total_cantidad = sum(item['cantidad'] for item in response.data)
        aplicar_descuento = total_cantidad > 4
        
        total_original = 0
        total_descuentos = 0
        
        # Process each product
        for producto in response.data:
            subtotal_original = producto['cantidad'] * producto['precio_unitario']
            total_original += subtotal_original
            
            # Calculate discount if applicable
            descuento = int(subtotal_original * 0.05) if aplicar_descuento else 0
            total_descuentos += descuento
            
            # Update product data
            producto['precio_original'] = subtotal_original
            producto['descuento'] = descuento
            producto['subtotal'] = subtotal_original - descuento
            producto['porcentaje_descuento'] = "5%" if aplicar_descuento else "0%"
            
            # Update database
            supabase.table('pedido_producto').update({
                'descuento': descuento,
                'subtotal': subtotal_original - descuento
            }).eq('id_pedido', id_pedido).eq('id_producto', producto['id_producto']).execute()
        
        return {
            "productos": response.data,
            "resumen": {
                "total_productos": total_cantidad,
                "aplicar_descuento": aplicar_descuento,
                "total_original": total_original,
                "total_descuentos": total_descuentos,
                "total_final": total_original - total_descuentos,
                "porcentaje_descuento": "5%" if aplicar_descuento else "0%"
            }
        }
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
        
        print(f"Intentando insertar producto {datos_producto['id_producto']} en pedido {datos_producto['id_pedido']}")
        
        try:
            check_existente = supabase.table('pedido_producto').select('id_pedido_producto').eq('id_pedido', datos_producto['id_pedido']).eq('id_producto', datos_producto['id_producto']).execute()
            if check_existente.data and len(check_existente.data) > 0:
                print(f"Producto ya existe en el pedido. Actualizando cantidad.")
                total_cantidad = sum(item['cantidad'] for item in existing_products.data)
                aplicar_descuento = total_cantidad > 4
                
                # Recalcular todos los productos del pedido
                all_products = supabase.table('pedido_producto').select('*').eq('id_pedido', datos_producto['id_pedido']).execute()
                
                if all_products.data:
                    for prod in all_products.data:
                        prod_subtotal = prod['cantidad'] * prod['precio_unitario']
                        prod_descuento = int(prod_subtotal * 0.05) if aplicar_descuento else 0
                        
                        supabase.table('pedido_producto').update({
                            'descuento': prod_descuento,
                            'subtotal': prod_subtotal - prod_descuento
                        }).eq('id_pedido', datos_producto['id_pedido']).eq('id_producto', prod['id_producto']).execute()
                
                # Actualizar el producto actual
                subtotal = datos_producto['cantidad'] * datos_producto['precio_unitario']
                descuento = int(subtotal * 0.05) if aplicar_descuento else 0
                
                update_data = {
                    "cantidad": datos_producto['cantidad'],
                    "precio_unitario": datos_producto['precio_unitario'],
                    "subtotal": subtotal - descuento,
                    "descuento": descuento
                }
                response = supabase.table('pedido_producto').update(update_data).eq('id_pedido', datos_producto['id_pedido']).eq('id_producto', datos_producto['id_producto']).execute()
                
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
async def agregar_multiples_productos(id_pedido: int, productos: ProductosEnPedido):
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

        # Calculate total quantity for discount
        total_cantidad = sum(p.cantidad for p in productos.productos)
        aplicar_descuento = total_cantidad > 4
        
        print(f"Total productos en pedido: {total_cantidad}, aplicar descuento: {aplicar_descuento}")
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
        
        print(f"Intentando insertar {len(productos_a_insertar)} productos en el pedido {id_pedido}")
        print(f"Primer producto: {productos_a_insertar[0] if productos_a_insertar else 'No hay productos'}")
        
        try:
            # Insert products
            response = supabase.table('pedido_producto').insert(productos_a_insertar).execute()
            
            if response.data:
                # After insertion, recalculate all discounts
                if aplicar_descuento:
                    # Update each product's discount and subtotal
                    for producto in response.data:
                        subtotal_original = producto['cantidad'] * producto['precio_unitario']
                        descuento = int(subtotal_original * 0.05)
                        subtotal_final = subtotal_original - descuento
                        
                        supabase.table('pedido_producto').update({
                            'descuento': descuento,
                            'subtotal': subtotal_final
                        }).eq('id_pedido', id_pedido).eq('id_producto', producto['id_producto']).execute()
                
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
async def actualizar_producto_en_pedido(id_pedido: int, id_producto: int, datos: PedidoProductoUpdate):
    try:
        supabase = get_conexion()
        
        check_existente = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        if not check_existente.data or len(check_existente.data) == 0:
            raise HTTPException(status_code=404, detail="El producto no existe en el pedido especificado")
        
        # Obtener todos los productos del pedido para calcular el total
        productos_pedido = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        total_cantidad = sum(item['cantidad'] for item in productos_pedido.data)
        
        # Si se está actualizando la cantidad, ajustar el total
        if datos.cantidad is not None:
            # Restar la cantidad anterior y sumar la nueva
            for prod in productos_pedido.data:
                if prod['id_producto'] == id_producto:
                    total_cantidad = total_cantidad - prod['cantidad'] + datos.cantidad
                    break
        
        aplicar_descuento = total_cantidad > 4
        
        # Preparar datos de actualización
        datos_actualizar = {k: v for k, v in datos.dict().items() if v is not None}
        
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Si se actualiza cantidad o precio, recalcular subtotal y descuento
        if 'cantidad' in datos_actualizar or 'precio_unitario' in datos_actualizar:
            producto_actual = check_existente.data[0]
            cantidad = datos_actualizar.get('cantidad', producto_actual['cantidad'])
            precio = datos_actualizar.get('precio_unitario', producto_actual['precio_unitario'])
            
            subtotal_final, descuento = calcular_descuento_producto(cantidad, precio, aplicar_descuento)
            
            datos_actualizar.update({
                'subtotal': subtotal_final,
                'descuento': descuento
            })
        
        response = supabase.table('pedido_producto').update(datos_actualizar).eq('id_pedido', id_pedido).eq('id_producto', id_producto).execute()
        
        # Recalcular descuentos para todos los productos después de la actualización
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

@router.post("/pedido/{id_pedido}/recalcular-descuentos")
async def recalcular_descuentos_pedido(id_pedido: int):
    try:
        supabase = get_conexion()
        
        # Get all products in the order
        response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontraron productos en el pedido")
        
        # Calculate total quantity to determine if discount applies
        total_cantidad = sum(item['cantidad'] for item in response.data)
        aplicar_descuento = total_cantidad > 4
        
        # Update each product's discount and subtotal
        actualizaciones = []
        for producto in response.data:
            subtotal_final, descuento = calcular_descuento_producto(
                producto['cantidad'],
                producto['precio_unitario'],
                aplicar_descuento
            )
            
            # Actualizar en la base de datos
            update_response = supabase.table('pedido_producto').update({
                'descuento': descuento,
                'subtotal': subtotal_final
            }).eq('id_pedido', id_pedido).eq('id_producto', producto['id_producto']).execute()
            
            if update_response.data:
                actualizaciones.append(update_response.data[0])
        
        # Verificar que todos los productos se actualizaron correctamente
        if len(actualizaciones) != len(response.data):
            raise HTTPException(status_code=500, detail="No se pudieron actualizar todos los descuentos")
        
        # Get updated products to verify changes
        updated_response = supabase.table('pedido_producto').select('*').eq('id_pedido', id_pedido).execute()
        
        # Verificar que los descuentos se aplicaron correctamente
        for producto in updated_response.data:
            if aplicar_descuento and producto['descuento'] == 0:
                print(f"Advertencia: Producto {producto['id_producto']} no tiene descuento aplicado")
        
        # Calcular totales
        total_subtotal = sum(prod['subtotal'] for prod in updated_response.data)
        total_descuento = sum(prod['descuento'] for prod in updated_response.data)
        total_sin_descuento = total_subtotal + total_descuento
        
        return {
            "mensaje": "Descuentos recalculados con éxito",
            "aplicar_descuento": aplicar_descuento,
            "total_productos": total_cantidad,
            "productos": updated_response.data,
            "resumen": {
                "total_sin_descuento": total_sin_descuento,
                "total_descuento": total_descuento,
                "total_final": total_subtotal,
                "porcentaje_descuento": "5%" if aplicar_descuento else "0%"
            }
        }
        
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(status_code=500, detail=str(ex))
