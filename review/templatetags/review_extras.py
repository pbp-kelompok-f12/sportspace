from django import template

register = template.Library()

@register.filter
def mask_username(username):
    if not username:
        return ""
    if len(username) <= 2:
        return username[0] + "*"*(len(username)-1)
    return username[0] + "*"*(len(username)-2) + username[-1]
