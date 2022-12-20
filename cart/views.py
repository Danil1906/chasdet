from decimal import Decimal

from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from mainstoreapp.models import Product, Profile, Price, Promocode, Order, OrderText
from users.forms import PromoForm
from .cart import Cart
from .forms import CartAddProductForm, CountryIndex, DeliveryForm, DeliveryPhoneForm
from django.shortcuts import *
from django.contrib.auth.models import User
import requests
from dadata import Dadata
from django.views.decorators.csrf import csrf_exempt

from .sms_prosto import smsRequest


@csrf_exempt
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    wholesale = False

    if request.user.is_authenticated:
        user = Profile.objects.filter(user=User.objects.get(username=request.user)).first()

        if user.wholesale:
            wholesale = True

        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product,
                     quantity=cd['quantity'],
                     update_quantity=cd['update'],
                     wholesale=wholesale)
            items_in_cart = len(cart.keys)
            data = {'count': items_in_cart}

            return JsonResponse(data)

    else:
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product,
                     quantity=cd['quantity'],
                     update_quantity=cd['update'],
                     wholesale=wholesale)
            items_in_cart = len(cart.keys)
            data = {'count': items_in_cart}

            return JsonResponse(data)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    items_in_cart = len(cart.keys)
    total_price = cart.get_total_price()

    data = {'count': items_in_cart,
            'total_price': total_price}

    return JsonResponse(data)


def remove_all(request, products_id):
    data = {'done': 'done'}
    products_id = products_id.split('-')
    products_id = [int(i) for i in products_id]

    cart = Cart(request)

    for i in products_id:
        product = get_object_or_404(Product, id=i)
        cart.remove(product)

    items_in_cart = len(cart.keys)
    total_price = cart.get_total_price()

    data = {'count': items_in_cart,
            'total_price': total_price}

    return JsonResponse(data)


def cart_detail(request):
    cart = Cart(request)
    form = CartAddProductForm()
    promo_form = PromoForm()

    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=User.objects.get(username=request.user)).first()
        return render(request, 'cart/detail.html',
                      {'cart': cart,
                       'profile': profile,
                       'form': form,
                       'promo_form': promo_form})
    else:
        return render(request, 'cart/detail.html',
                      {'cart': cart,
                       'form': form,
                       'promo_form': promo_form})


def order(request, retail=None):
    discount_in_percent = False
    discount_in_the_money = False

    form = CountryIndex()
    delivery_form = DeliveryForm()
    delivery_phone = DeliveryPhoneForm()
    cart = Cart(request)
    delivery_and_minimum = Price.objects.all().first()
    sum_total = 0
    retail = retail
    retail_prices = 0
    products = Product.objects.all()
    not_enough_available_quantity = {}
    data = {'delivery': delivery_and_minimum, 'sum_total': sum_total}
    mark = '<a class="btn btn-outline-danger mt-3" href="order/final/retail">Продолжить покупку по розничной цене</a>'

    if request.method == 'POST':
        promo_form = PromoForm(request.POST)
        if promo_form.is_valid():
            cf = promo_form.cleaned_data

            if Promocode.objects.filter(type_of_promo='DISCOUNT').exists():
                promo = Promocode.objects.all().filter(type_of_promo='DISCOUNT')
            else:
                promo = False

            if promo:
                user_promo = cf["promo"].upper()
                for i in promo:
                    bd_promo = i.promo
                    bd_promo = bd_promo.upper()
                    if user_promo == bd_promo:
                        if i.discount > 0:
                            discount_in_percent = i.discount
                            break
                    elif user_promo != bd_promo and user_promo != '':
                        discount_in_percent = 'fail'
            else:
                discount_in_percent = 'fail'

            # Добавление скидки в модель корзины для передачи данных представлению payment
            for i in cart:
                product = Product.objects.get(id=i['product'].id)

                cart.add_discount(discount_in_percent, product)

    if cart.get_total_price() != 0:
        list_items_for_order_page = []
        for i in cart:
            prod = products.get(title=i["product"].title)
            if int(i["quantity"]) <= prod.quantity:
                list_items_for_order_page.append(f'{i["product"].title} x {i["quantity"]} шт.')
            else:
                not_enough_available_quantity[i["product"].title] = [prod.quantity, i["quantity"], i["product"].id]
        # Проверяю доступное кол во товаров при попытке перейти на оформление
        if not_enough_available_quantity:

            error_prod_quantity = ''
            for k, v in not_enough_available_quantity.items():
                error_prod_quantity += f'{k} - запрошено {v[1]} шт., доступно {v[0]} шт. <br>'

            messages.error(request, f'''С момента добавления товара в корзину до момента
            оформления заказа доступное количество некоторых товаров изменилось.<br>
            Можете изменить количество по следующим товарам на доступное или удалить их из 
            корзины.<br><br>
            {error_prod_quantity}<br>
            ''')
            return redirect('cart_detail')
        else:
            if not retail == 'retail':
                if request.user.is_authenticated:
                    user = Profile.objects.filter(user=User.objects.get(username=request.user)).first()
                    if user.wholesale:
                        if cart.get_total_price() < delivery_and_minimum.min_sum_for_wholesale:
                            whole_prices = []
                            for i in cart:

                                # Меняю значение в корзине для передачи ей представлению payment
                                # для следующего высчета суммы заказа
                                product = Product.objects.get(id=i['product'].id)
                                cart.change_recalculation(True, product)

                                if 'full_price' in i.keys():
                                    retail_prices += Decimal(i['full_price']) * i['quantity']
                                    whole_prices.append(True)
                                else:
                                    retail_prices += i['price'] * i['quantity']

                            if True in whole_prices:
                                messages.error(request, f'''Минимальная сумма для заказа по оптовым ценам 
                                {delivery_and_minimum.min_sum_for_wholesale} руб. <br>
                                Дополните пожалуйста корзину или можем отпустить товары по розничным ценам. <br> 
                                Перерасчет вашей корзины по розничным ценам {retail_prices} руб. <br> {mark}''')
                                return redirect('cart_detail')
                            else:
                                sum_total = cart.get_total_price()
                                if discount_in_percent and isinstance(discount_in_percent, int):
                                    discount_in_the_money = round(sum_total - ((sum_total / 100) * discount_in_percent),
                                                                  2)
                                return render(request, 'cart/order.html',
                                              {'delivery': delivery_and_minimum,
                                               'sum_total': sum_total,
                                               'list_items': list_items_for_order_page,
                                               'form': form,
                                               'profile': user,
                                               'delivery_form': delivery_form,
                                               'phone_form': delivery_phone,
                                               'discount_in_percent': discount_in_percent,
                                               'sum_with_discount': discount_in_the_money})

                        else:
                            sum_total = cart.get_total_price()
                            if discount_in_percent and isinstance(discount_in_percent, int):
                                discount_in_the_money = round(sum_total - ((sum_total / 100) * discount_in_percent), 2)
                            return render(request, 'cart/order.html',
                                          {'delivery': delivery_and_minimum,
                                           'sum_total': sum_total,
                                           'list_items': list_items_for_order_page,
                                           'form': form,
                                           'profile': user,
                                           'delivery_form': delivery_form,
                                           'phone_form': delivery_phone,
                                           'discount_in_percent': discount_in_percent,
                                           'sum_with_discount': discount_in_the_money})
                    else:
                        sum_total = cart.get_total_price()
                        if discount_in_percent and isinstance(discount_in_percent, int):
                            discount_in_the_money = round(sum_total - ((sum_total / 100) * discount_in_percent), 2)
                        return render(request, 'cart/order.html',
                                      {'delivery': delivery_and_minimum,
                                       'sum_total': sum_total,
                                       'list_items': list_items_for_order_page,
                                       'form': form,
                                       'profile': user,
                                       'delivery_form': delivery_form,
                                       'phone_form': delivery_phone,
                                       'discount_in_percent': discount_in_percent,
                                       'sum_with_discount': discount_in_the_money})
                    # If the user is not logged in
                else:
                    if discount_in_percent and isinstance(discount_in_percent, int):
                        discount_in_the_money = round(sum_total - ((sum_total / 100) * discount_in_percent), 2)
                    return render(request, 'cart/order.html',
                                  {'delivery': delivery_and_minimum,
                                   'sum_total': cart.get_total_price(),
                                   'list_items': list_items_for_order_page,
                                   'form': form,
                                   'delivery_form': delivery_form,
                                   'phone_form': delivery_phone,
                                   'discount_in_percent': discount_in_percent,
                                   'sum_with_discount': discount_in_the_money})
                # (If the user is a wholesaler and did not fill the cart for the set amount,
                # decided to buy at retail prices in the appropriate notification)
            else:

                user = request.user
                if request.user.is_authenticated:
                    user = Profile.objects.filter(user=User.objects.get(username=request.user)).first()

                for i in cart:

                    if 'full_price' in i.keys():
                        retail_prices += Decimal(i['full_price']) * i['quantity']
                    else:
                        retail_prices += i['price'] * i['quantity']
                if discount_in_percent and isinstance(discount_in_percent, int):
                    discount_in_the_money = round(sum_total - ((sum_total / 100) * discount_in_percent), 2)
                return render(request, 'cart/order.html',
                              {'delivery': delivery_and_minimum,
                               'sum_total': retail_prices,
                               'list_items': list_items_for_order_page,
                               'form': form,
                               'profile': user,
                               'delivery_form': delivery_form,
                               'phone_form': delivery_phone,
                               'discount_in_percent': discount_in_percent,
                               'sum_with_discount': discount_in_the_money})
    else:
        messages.error(request, '''Корзина пуста''')
        return redirect('cart_detail')


def delivery(request):
    token = "b53d1bb0861825aa1d45d5c3d3c579cef395d97d"
    dadata = Dadata(token)
    data = {'pochta': {}, 'cdek': []}
    index = 0

    if request.method == 'POST':
        form = CountryIndex(request.POST)
        if form.is_valid():
            mail = form.cleaned_data
            index = mail['index']

    data = {'cdek': {"type": "FeatureCollection", "features": []}, 'full_cdek': [], 'pochta': {}}

    if len(str(index)) == 6:
        index = str(index)
        result = dadata.find_by_id("postal_office", index)
        region = result[0]['data']['region']
        city = result[0]['data']['city']

        data['pochta'] = {'index': index, 'region': region, 'city': city}

    cdek = requests.get(f'http://integration.cdek.ru/pvzlist/v1/json?citypostcode={index}')
    cdek = cdek.json()
    dex = 0

    if cdek['pvz'] != []:
        for i in cdek['pvz']:
            if i["status"] == 'ACTIVE' and i['type'] == 'PVZ':
                data['cdek']['features'].append({"type": "Feature", "id": dex, "geometry": {"type": "Point",
                                                                                            "coordinates": [i["coordY"],
                                                                                                            i[
                                                                                                                "coordX"]]},
                                                 "properties": {
                                                     "balloonContentBody": f"<p id='ya-p-text'>{i['fullAddress']}</p>"}})

                data['full_cdek'].append({'id': dex, 'full_address': i['fullAddress'], 'address': i['address'],
                                          'coordinates': [i["coordY"], i["coordX"]], 'index': i['postalCode'],
                                          'region': i['regionName'], 'city': i['city']})
                dex += 1
    if data['pochta']:
        if not data['pochta']['city']:
            data['pochta']['city'] = cdek['pvz'][0]['city']

    return JsonResponse(data)


def payment(request, delivery_type=0):
    data = {}

    # Получение цены на доставку
    delivery_price = Price.objects.get()
    delivery_price_cdek = int(delivery_price.sdek_delivery_price)
    delivery_price_pochta = int(delivery_price.poshta_delivery_price)

    cart = Cart(request)

    # Определение скидки
    discount = None
    wholesaler_at_full_price = False
    for i in cart:
        if i['recalculation']:
            wholesaler_at_full_price = True
            break

        if i['discount'] > 0:
            dis = i['discount']
            discount = dis
            break

    # Получаем корзину пользователя, формируется список товаров и итоговая сумма
    total_price = 0
    cart_items = {}
    for i in cart:
        if wholesaler_at_full_price:
            if 'full_price' in i.keys():
                print(i['full_price'])
                print(type(i['full_price']))
                print(Decimal(i['full_price']))
                print(type(Decimal(i['full_price'])))
                total_price += float(i['full_price']) * i['quantity']
                cart_items[i['product'].title] = i['quantity']
            else:
                total_price += float(i['price']) * i['quantity']
                cart_items[i['product'].title] = i['quantity']
        else:
            total_price += i['price'] * i['quantity']
            cart_items[i['product'].title] = i['quantity']

    if discount and discount > 0:
        total_price = round(int(total_price) * (1 - (discount / 100)), 2)

    if request.user.is_authenticated:
        # Наполнение data для json ответа на кнопка авто заполенения данных в форму отправления
        profile = Profile.objects.get(user=User.objects.get(username=request.user))
        profile_address_cdek = profile.cdek_address
        profile_address_pochta = profile.pochta_address
        profile_phone = profile.phone
        profile_email = profile.email
        profile_fio = profile.fio

        profile_phone = str(profile_phone)

        data['fio'] = profile_fio
        data['phone'] = profile_phone
        data['email'] = profile_email
        data['cart_items'] = cart_items
        data['discount'] = discount

    # Checking existing data in the user 's delivery address database
    if delivery_type == 1:
        data['address'] = profile_address_cdek
        total_price += delivery_price_cdek
        data['total_price'] = total_price

        return JsonResponse(data)

    elif delivery_type == 2:
        data['address'] = profile_address_pochta
        total_price += delivery_price_pochta
        data['total_price'] = total_price

        return JsonResponse(data)

    else:

        if request.method == 'POST':
            form_phone = DeliveryPhoneForm(request.POST)
            form_adress = DeliveryForm(request.POST)
            if form_phone.is_valid() and form_adress.is_valid():
                data1 = form_phone.cleaned_data
                data2 = form_adress.cleaned_data
                # indata это скрытое поле по которому смогу понимать какая доставка выбрана и соответственно считать спокойно на
                # беке сумму достав

                # Вся логика. Тут сохранение данных в БД, отправка писем на почты, смс.
                region = data2['region']
                city = data2['city']
                street = data2['street']
                full_name = data2['full_name']
                email = data2['email']
                num_phone = str(data1['phone'])
                address = f'{region} - {city} - {street}'
                type_delivery = int(data2['name_delivery'])

                # Созранение данных адреса для дальнейшего автоматического подставления
                # в случае если пользователь авторизован
                if request.user.is_authenticated:
                    if type_delivery == 1:
                        if len(profile.cdek_address) > 0:
                            pass
                        else:
                            profile.cdek_address = address
                            profile.save()
                    elif type_delivery == 2:
                        if len(profile.pochta_address) > 0:
                            pass
                        else:
                            profile.pochta_address = address
                            profile.save()

                # Сформировать заказ и добавить его в модель заказов
                if int(type_delivery) == 1:
                    delivery_for_model = 'CDEK'
                    total_price += delivery_price_cdek
                elif int(type_delivery) == 2:
                    delivery_for_model = 'POCHTA'
                    total_price += delivery_price_pochta

                if discount is None:
                    discount = 0

                cart_items_str = ''
                for k, v in cart_items.items():
                    cart_items_str += f'{k} х {v} шт\n'

                order_model = Order(
                    type_delivery=delivery_for_model,
                    address=address,
                    email=email,
                    phone=num_phone,
                    cart=cart_items_str,
                    discount=discount,
                    total_sum=total_price,
                )
                order_model.save()

                # Отправление уведомлений на почту администратору и покупателю
                message = OrderText.objects.all().first()
                order_number = order_model.order_num

                user_message_title = message.title
                user_message_text = message.first_info.replace('&', str(order_number))
                user_message_email = email

                admin_email = message.email
                admin_message_title = f'Новый заказ №{order_number}'
                admin_message_text = ''
                admin_message_text += num_phone + '\n' + email + '\n' + str(
                    total_price) + '\n' + cart_items_str + '\n' + address + '\n' + delivery_for_model

                # Отправление уведомления администратору

                try:
                    send_mail(
                        admin_message_title,
                        admin_message_text,
                        'chasdetal@gmail.com',
                        [admin_email],
                        fail_silently=False,
                    )
                except BaseException:
                    data['redirect'] = reverse('#')
                    messages.error(request,
                                   'Что то не так. Заказ не был оформлен')
                #
                # # Отправление уведомления покупателю

                try:
                    send_mail(
                        user_message_title,
                        user_message_text,
                        'chasdetal@gmail.com',
                        [user_message_email],
                        fail_silently=False,
                    )
                except BaseException:
                    data['redirect'] = reverse('#')
                    messages.error(request,
                                   'Что то не так. Заказ не был оформлен')

                num_phone_for_sms = ''
                for i in num_phone:
                    if i.isdigit():
                        num_phone_for_sms += i

                num_phone_for_sms = int(num_phone_for_sms)

                try:
                    sender = smsRequest('en141899', '978313')
                    sender.send(num_phone_for_sms, user_message_text)
                except BaseException:
                    data['redirect'] = reverse('#')
                    messages.error(request,
                                   'Что то не так. Заказ не был оформлен')

                products = Product.objects.all()

                cart_items_str = ''
                for i in products:
                    if i.title in cart_items.keys():
                        one_prod = products.get(title=i.title)
                        if one_prod.quantity >= cart_items[i.title]:
                            one_prod.quantity -= cart_items[i.title]
                            cart_items_str += f'{i.title} х {cart_items[i.title]} шт\n'
                            if request.user.is_authenticated:
                                # {product_id:{rate:review}}
                                purchased = profile.purchased
                                if i.id not in purchased.keys():
                                    purchased[i.id] = {'': ''}
                                    profile.save()

                            one_prod.save()
                        else:
                            much_as_there = one_prod.quantity
                            much_as_wants = cart_items[i.title]
                            one_prod.quantity = 0
                            cart_items_str += f'{i.title} х {much_as_wants} шт--{much_as_there}\n'
                            if request.user.is_authenticated:
                                # {product_id:{rate:review}}
                                purchased = profile.purchased
                                if i.id not in purchased.keys():
                                    purchased[i.id] = {'': ''}
                                    profile.save()

                            one_prod.save()

                order_model.cart = cart_items_str
                order_model.save()

                # Удаление товара из сессии
                cart.clear()

                messages.success(request,
                                 'Заказ успешно оформлен. Дополнительные данные поступят вам на email и на указанный при оформлении номер')
                data['redirect'] = reverse('home')
            else:
                data['redirect'] = reverse('#')
                messages.error(request,
                               'Что то не так. Заказ не был оформлен')

    return JsonResponse(data)
