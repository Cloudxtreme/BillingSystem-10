from django import template
register = template.Library()

@register.filter
def lessThan(a,b):
    if b=="all":
        return True
    if int(a) < int(b):
        return True
    else:
        return False

@register.filter
def lookup(d, key):
    return d[key]

@register.filter
def add_num(a, b):
    return a+int(b)

@register.filter
def times(number):
    return range(int(number))

@register.filter
def get_corresponding_text(b):
    if b=="+":
        return "Created"
    elif b=="-":
        return "Deleted"
    elif b=="~":
        return "Modified"
    else:
        return "---"

@register.filter
def getField(form, arg):
    try:
        return form[arg]
    except:
        return ''

@register.filter
def getFieldId(form, arg):
    try:
        return form[arg].auto_id
    except:
        return ''

@register.filter
def prePlusConcat(value, arg):
    try:
        return str(value) + str(arg+1)
    except:
        return str(value) + str(arg)

