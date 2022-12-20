from django import template
from cart.cart import Cart

register = template.Library()


@register.simple_tag()
def in_cart(request):
    cart = Cart(request)
    items_in_cart = len(cart.keys)
    return items_in_cart
