import copy
from decimal import Decimal
from django.conf import settings
from mainstoreapp.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.keys = self.cart.keys()

    def add(self, product, quantity=1, update_quantity=False, wholesale=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.id)
        if wholesale:
            if product.wholesale_price:
                if product_id not in self.cart:
                    self.cart[product_id] = {'quantity': 0,
                                             'price': str(product.wholesale_price),
                                             'full_price': str(product.price),
                                             'discount': 0,
                                             'recalculation': False}
            else:
                if product_id not in self.cart:
                    self.cart[product_id] = {'quantity': 0,
                                             'price': str(product.price),
                                             'discount': 0,
                                             'recalculation': False}
        else:
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': 0,
                                         'price': str(product.price),
                                         'discount': 0,
                                         'recalculation': False}

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def change_recalculation(self, boolValue, product):
        product_id = str(product.id)
        self.cart[product_id]['recalculation'] = boolValue

        self.save()

    def add_discount(self, discount, product):
        product_id = str(product.id)
        self.cart[product_id]['discount'] = discount

        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product):
        """
        Удаление товара из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.all().filter(id__in=product_ids)
        cart_copy = copy.deepcopy(self.cart)
        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
