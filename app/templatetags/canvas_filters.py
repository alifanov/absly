from django import template

register = template.Library()

def by_user(qs, user):
    return qs.filter(user=user)

register.filter('by_user', by_user)