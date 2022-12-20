from django import template
from mainstoreapp.models import Product, Category
import mainstoreapp
from django.core.cache import cache

register = template.Library()


@register.inclusion_tag('mainstoreapp/bread_tag.html', takes_context=True)
def breadcrumb(context):
    data = None
    id = context['id']
    all_categories = Category.objects.all()
    slug = all_categories.get(id=id).slug
    if context['cat_or_prod']:
        one_obj_from_data = context['cat_or_prod'][0]
    else:
        one_obj_from_data = None
    title_to_bread_for_product_vews_page = None
    slug_for_product = False
    cslug = False
    empty_cat = False

    if isinstance(one_obj_from_data, Category):
        data = one_obj_from_data.get_ancestors()
    elif isinstance(one_obj_from_data, Product):
        category = one_obj_from_data.category

        categories = all_categories.select_related('parent')
        if category.is_child_node():
            data = category.get_ancestors()
            slug_for_product = True
            title_to_bread_for_product_vews_page = categories.get(id=context['id'])

            if isinstance(context['view'], mainstoreapp.views.DetailProductView):
                cslug = context['product'].title
        else:
            data = category
    else:

        category = cache.get('category_bread')
        if not category:
            category = all_categories.filter(id=context["id"]).first()
            cache.set('category_bread', category, 60 * 60)

        data = category.get_ancestors()
        title_to_bread_for_product_vews_page = category.title
        empty_cat = True

    return {'ancestors': data,
            'title_for_prod': title_to_bread_for_product_vews_page,
            'slug_for_product': slug_for_product,
            'slug': slug,
            'cslug': cslug,
            'empty_cat': empty_cat}


'''Данной замороченный тег служит для формирования хлебных крошек. Причина такого решения - использование mppt дерева
и одного динамического шаблона для 2х модель одновременно. Данный тег всего лишь на основании принятых данных, делает
вывод какая именно это таблица и какая ситуация. Если это модель категорий, то одно, если это модель товаров в списке товаров,
то другое а если это модель товаров на отдельной страничке товара, то третье. В шаблоне bread_tag.html соответствующие 
развитвления с упором на булевые.'''