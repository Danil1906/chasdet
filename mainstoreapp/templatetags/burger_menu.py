from django import template
from mainstoreapp.models import Product, Category
from django.core.cache import cache

register = template.Library()


@register.inclusion_tag('mainstoreapp/burger_tag.html')
def burger():
    categories = cache.get('category_burger')
    if not categories:
        categories = Category.objects.all()
        cache.set('category_burger', categories, 60 * 60)

    offers = cache.get('offers_burger')
    if not offers:
        offers = Product.objects.filter(special_offer=True, is_published=True)
        cache.set('offers_burger', offers, 60 * 60)

    return {'categories': categories, 'offers': offers}
