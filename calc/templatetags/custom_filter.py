from django import template

register = template.Library()


@register.filter(name="lookup")
def lookup(d, key):
    """use as  {{ mylist|lookup:x }}"""
    return d[key]
