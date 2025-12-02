from django import template

register = template.Library()

@register.filter(name="dividir")
def dividir(field, attr):
    try:
        return "{:.0f}".format(field / attr)
    except Exception as e:
        print("ERROR dividir:", e)
        return 0


@register.filter(name="dividir_promedio")
def dividir_promedio(field, attr):
    try:
        return "{:.0f}".format(field / attr)
    except Exception as e:
        print("ERROR dividir_promedio:", e)
        return 0
