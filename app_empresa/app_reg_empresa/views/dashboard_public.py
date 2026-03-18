from django.views.generic import TemplateView
from django_tenants.utils import schema_context
from app_empresa.app_reg_empresa.models import Empresa, PeriodoFiscal


class DashboardPublicView(TemplateView):

    template_name = "public/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        with schema_context("public"):
            empresas = Empresa.objects.all()
            periodos = PeriodoFiscal.objects.all()

        context["empresas"] = empresas
        context["periodos"] = periodos

        return context