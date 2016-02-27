from django import template
register = template.Library()


@register.filter
def lookup(d, key):
    return d[key]

@register.filter
def add_num(a, b):
	print "asdfasdfadsfasdfasdf" 
	print a, b
	return a+int(b)
