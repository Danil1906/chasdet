from django import template
from mainstoreapp.models import Social, Contact
from django.core.cache import cache

register = template.Library()


@register.simple_tag()
def contact_info():
    contact = cache.get('contact_info')
    if not contact:
        contact = Contact.objects.first()
        cache.set('contact_info', contact, 60 * 60 * 24)

    link = cache.get('footer_social')
    if not link:
        link = Social.objects.first()
        cache.set('footer_social', link, 60 * 60 * 24)

    return {'contact': contact, 'link': link}
