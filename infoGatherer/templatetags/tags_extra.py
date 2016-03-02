from django import template
register = template.Library()


@register.filter
def lookup(d, key):
    return d[key]

@register.filter
def add_num(a, b):
    return a+int(b)

@register.filter
def getField(form, arg):
    try:
        return form[arg]
    except:
        return ''

@register.filter
def prePlusConcat(value, arg):
    try:
        return str(value) + str(arg+1)
    except:
        return str(value) + str(arg)