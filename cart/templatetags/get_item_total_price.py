from django import template
from decimal import Decimal


register = template.Library()


@register.simple_tag()
def total_price(qtt, price):

    return Decimal(qtt * price)
