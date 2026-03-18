from django.views.generic import *
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.db import transaction

from app_empresa.app_reg_empresa.models import PeriodoFiscal, Empresa, Domain


class PeriodoFiscalCreateView(CreateView):

    model = PeriodoFiscal
    fields = ["empresa", "anio"]

    template_name = "public/periodo_form.html"

    success_url = reverse_lazy("app_empresa:periodo_list")

    def form_valid(self, form):

        with transaction.atomic():

            empresa = form.cleaned_data["empresa"]
            anio = form.cleaned_data["anio"]

            schema = f"{empresa.schema_name}_{anio}"

            tenant = PeriodoFiscal.objects.create(
                empresa=empresa,
                anio=anio,
                schema_name=schema
            )

            Domain.objects.create(
                domain=f"{schema}.localhost",
                tenant=tenant,
                is_primary=True
            )

            messages.success(
                self.request,
                f"Periodo {anio} creado correctamente"
            )

        return super().form_valid(form)


class PeriodoFiscalListView(ListView):

    model = PeriodoFiscal

    template_name = "public/periodo_list.html"

    context_object_name = "periodos"