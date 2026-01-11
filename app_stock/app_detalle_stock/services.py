from crum import get_current_user
from django.db import transaction
from .models import Total_Stock, Producto_Stock
from app_contabilidad_planCuentas.models import EncabezadoCuentasPlanCuenta, DetalleCuentasPlanCuenta
from app_stock.app_detalle_stock.models import Total_Stock, Producto_Stock

@transaction.atomic
def registrar_movimiento_stock(
    *,
    producto_empresa,
    tipo,
    cantidad,
    invoice=None,
    proveedor=None,
    piscinas=None,
    numero_guia=None,
    responsable=None,
    detalle_dieta_id=None
):

    stock = Total_Stock.objects.select_for_update().get(pk=producto_empresa.pk)

    if tipo == 'INGRESO':
        stock.stock += cantidad
        ingreso = cantidad
        egreso = 0

    elif tipo == 'EGRESO':
        if stock.stock < cantidad:
            raise ValueError('Stock insuficiente')
        stock.stock -= cantidad
        ingreso = 0
        egreso = cantidad

    else:
        raise ValueError('Tipo inválido')

    stock.save()

    Producto_Stock.objects.create(
        invoice_stock=invoice,
        producto_empresa=stock,
        tipo=tipo,
        cantidad_ingreso=ingreso,
        cantidad_egreso=egreso,
        proveedor=proveedor,
        piscinas=piscinas,
        numero_guia=numero_guia,
        responsable_ingreso=responsable,
        detalle_dieta_id=detalle_dieta_id,
        activo=True
    )


def eliminar_asientos_por_detalle(detalle_id):
    encabezados = EncabezadoCuentasPlanCuenta.objects.filter(
        comprobante__icontains=f"EGR-DET-{detalle_id}"
    )

    for e in encabezados:
        DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan=e).delete()
        e.delete()


def revertir_stock_por_detalle(detalle, texto_guia):
    datos = []

    if detalle.balanceado:
        datos.append((detalle.balanceado.id, detalle.cantidad))
    if detalle.insumo1:
        datos.append((detalle.insumo1, detalle.gramaje1))
    if detalle.insumo2:
        datos.append((detalle.insumo2, detalle.gramaje2))
    if detalle.insumo3:
        datos.append((detalle.insumo3, detalle.gramaje3))
    if detalle.insumo4:
        datos.append((detalle.insumo4, detalle.gramaje4))

    for prod_id, cantidad in datos:
        if not prod_id or cantidad <= 0:
            continue

        ps = Total_Stock.objects.filter(
            nombre_empresa_id=detalle.piscinas.empresa_id,
            nombre_prod_id=prod_id
        ).first()

        if not ps:
            continue

        Producto_Stock.objects.create(
            producto_empresa_id=ps.pk,
            tipo='INGRESO',
            piscinas=detalle.piscinas.numero,
            cantidad_ingreso=float(cantidad),
            fecha_ingreso=detalle.dieta.fecha,
            numero_guia=texto_guia,
            responsable_ingreso=get_current_user(),
            activo=False,
            detalle_dieta_id=detalle.pk
        )



