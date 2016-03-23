from django import template
register = template.Library()


@register.filter
def indexList(List, i):
    return List[int(i)]

@register.filter
def indexDict(Dict, i):
    return Dict.get(i)
