from pydantic import BaseModel
from typing import Optional, List

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

class ResumenDescuentos(BaseModel):
    total_productos: int
    aplicar_descuento: bool
    total_original: int
    total_descuentos: int
    total_final: int
    porcentaje_descuento: str

class PedidoProductoResponse(PedidoProductoBase):
    id_pedido_producto: int
    precio_original: Optional[int]
    porcentaje_descuento: Optional[str]

class PedidoProductoListResponse(BaseModel):
    productos: List[PedidoProductoResponse]
    resumen: ResumenDescuentos
