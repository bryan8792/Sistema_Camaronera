from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime
from django.db import transaction

from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock
from app_contabilidad_planCuentas.models import (
    EncabezadoCuentasPlanCuenta,
    DetalleCuentasPlanCuenta
)


@receiver(post_save, sender=Producto_Stock)
def crear_asiento_contable_egreso(sender, instance, created, **kwargs):

    if not created:
        return

    if instance.tipo != 'EGRESO':
        return

    if not instance.detalle_dieta_id:
        return

    piscina = instance.piscinas
    if not piscina:
        return

    empresa = getattr(piscina, 'empresa', None)
    if not empresa:
        return

    comprobante = f"EGR-DET-{instance.detalle_dieta_id}"

    print("\n" + "=" * 60)
    print("[CONTABILIDAD] RECONSTRUYENDO ASIENTO DE DIETA")
    print("=" * 60)

    with transaction.atomic():

        EncabezadoCuentasPlanCuenta.objects.filter(
            comprobante=comprobante,
            empresa=empresa
        ).delete()

        movimientos = Producto_Stock.objects.filter(
            detalle_dieta_id=instance.detalle_dieta_id,
            tipo='EGRESO',
            activo=True
        ).select_related('producto_empresa__nombre_prod')

        if not movimientos.exists():
            return

        total_egreso = 0
        valores = []

        for mov in movimientos:
            producto = mov.producto_empresa.nombre_prod
            cantidad = float(mov.cantidad_egreso or 0)
            costo = float(producto.costo_aplicacion or 0)

            # ✅ LÓGICA SEGURA
            valor = cantidad * costo if costo > 0 else cantidad

            if valor <= 0:
                continue

            valores.append((mov, producto, valor))
            total_egreso += valor

        if total_egreso <= 0:
            return

        cuenta_suministros = getattr(piscina, 'cuenta_suministros', None)
        if not cuenta_suministros:
            return

        encabezado = EncabezadoCuentasPlanCuenta.objects.create(
            codigo=int(datetime.now().timestamp()),
            tip_cuenta='5',
            tip_transa='EGRESO',
            fecha=instance.fecha_ingreso or timezone.now().date(),
            comprobante=comprobante,
            descripcion=f"Consumo Dieta Piscina {piscina}",
            empresa=empresa,
            reg_control='RT'
        )

        # DEBE – SUMINISTROS
        DetalleCuentasPlanCuenta.objects.create(
            encabezadocuentaplan=encabezado,
            orden=1,
            cuenta=cuenta_suministros,
            detalle=f"Consumo dieta {piscina}",
            debe=round(total_egreso, 2),
            haber=0,
            origen='STOCK'
        )

        orden = 2

        for mov, producto, valor in valores:

            stock_total = Total_Stock.objects.filter(
                nombre_prod=producto,
                nombre_empresa=empresa
            ).first()

            if not stock_total or not stock_total.plan_cuenta:
                continue

            DetalleCuentasPlanCuenta.objects.create(
                encabezadocuentaplan=encabezado,
                orden=orden,
                cuenta=stock_total.plan_cuenta,
                detalle=f"Egreso inventario {producto}",
                debe=0,
                haber=round(valor, 2),
                origen='STOCK'
            )

            orden += 1

        print(f"[CONTABILIDAD] Asiento contable correcto ({comprobante})")
