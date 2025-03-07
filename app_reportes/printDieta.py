
from Sistema_Camaronera.wsgi import *
from django.template.loader import get_template
from weasyprint import HTML


def printDieta():
    template = get_template("app_reportes/printDieta.html")
    context = {"name": "Pdf de Dieta"}
    html_template = template.render(context)
    HTML(string=html_template).write_pdf(target="dieta.pdf")

printDieta()