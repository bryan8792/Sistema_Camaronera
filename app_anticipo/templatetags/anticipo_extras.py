from django import template

register = template.Library()

@register.filter
def split_form_fields(form, cols):
    """
    Divide los campos del formulario en grupos de columnas
    Uso: {% for fields in form|split_form_fields:4 %}
    """
    fields = list(form)
    result = []
    for i in range(0, len(fields), int(cols)):
        result.append(fields[i:i + int(cols)])
    return result
