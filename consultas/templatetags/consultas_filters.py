from django import template

register = template.Library()


@register.filter
def count_words(text):
    return len(text.split())
