import datetime
import os
import uuid

from django.core.mail import send_mail
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from django.core.files.base import ContentFile
import io

from cart.sms_prosto import smsRequest


def sendEmailAndSms(user_message_title, user_message_text, user_message_email, phone, sender_name='ChasDetal'):
    send_mail(
        user_message_title,
        user_message_text,
        'chasdetal@gmail.com',
        [user_message_email],
        fail_silently=False,
    )

    phone = phone.as_international

    sender = smsRequest('en141899', '978313')
    request = (sender.send(phone, user_message_text, sender_name))

    return request


# Кастумные поля

class WEBPFieldFile(ImageFieldFile):

    def save(self, name, content, save=True):
        content.file.seek(0)
        image = Image.open(content.file)
        image_bytes = io.BytesIO()
        image.save(fp=image_bytes, format="WEBP")
        image_content_file = ContentFile(content=image_bytes.getvalue())
        super().save(name, image_content_file, save)


class WEBPField(models.ImageField):
    attr_class = WEBPFieldFile


def image_folder_category(instance, filename):
    now = datetime.datetime.now()
    return f'{str(now.year)}/{str(now.month)}/{str(now.day)}/{uuid.uuid4().hex}.webp'


# Create your models here.
class Category(MPTTModel):
    title = models.CharField(max_length=50, verbose_name='Название категории')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            verbose_name='Связи/ Категория/ Подкатегория',
                            on_delete=models.CASCADE)
    photo = WEBPField(upload_to=image_folder_category, blank=True, default='default.webp')
    slug = models.SlugField(verbose_name='url')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug, 'id': self.id})

    class MPTTMeta:
        order_insertion_by = ['title']

    def save(self, *args, **kwargs):
        super().save()

        # Так можно получить название файла
        image = Image.open(self.photo.path)

        name = os.path.split(self.photo.path)[1].split('.')[0]

        if name != 'default':
            if image.height > 400 or image.width > 400:
                resize = (400, 400)
                image.thumbnail(resize)

                image.save(self.photo.path)
                super().save()
            else:

                image.save(self.photo.path)
                super().save()

    class Meta:
        ordering = ['title']
        verbose_name = 'Категория(ю)'
        verbose_name_plural = 'Категории'


class PrivacyPolicy(models.Model):
    text = models.TextField(verbose_name='Политика', default=' ')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Политики конфиденциальности'
        verbose_name_plural = 'Политики конфиденциальности'


def image_folder_product(instance, filename):
    now = datetime.datetime.now()
    return f'photos/{str(now.year)}/{str(now.month)}/{str(now.day)}/{uuid.uuid4().hex}.webp'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(max_length=255, verbose_name='url', unique=True)
    # Бланк это обязательность поля, если стоит тру то заполнение не обязательно, для поля контента принято делать так
    description = models.TextField(blank=True, verbose_name='Описание')
    # Аплоад ту, куда сохранять картинки, ну и дальше папка с синтаксисом который создаст в ней папку год, месяца и дня
    photo = WEBPField(upload_to=image_folder_product, blank=True, default='default_prod_black.webp')
    # Если модель на которую ссылкаемся объявлена раньше то можно просто ссылать на нее, если же нет, то указывать нужно
    # как строку
    # Релейтед нейм это для свойства set не до конца помню точно что это такое
    category = TreeForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='Категория')
    quantity = models.IntegerField(verbose_name='Количество', default=1)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано?')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(verbose_name='Цена для оптовика', max_digits=10, decimal_places=2, blank=True,
                                          null=True)

    old_price = models.DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        verbose_name='Старая цена (для акций или распродаж)',
        null=True,
        help_text='''Поле для отображения старой цена. Для заполнения не обязательно. В случае если
        цена на товар снижена, указать сюда старую цена а поле "Цена" указать новую, в таком случае на сайте старый 
        ценник будет перечеркнут. В случае если цена наоборот повысилась, это поле затрагивать не нужно.
        ВАЖНО! Цена которую заплатит клиент указывается в поле "Цена", не перепутать!'''
    )

    glass = models.BooleanField(default=False, verbose_name='Стекло', help_text='''Этот флаг создан для товаров "стекла". Его активация
    делает отображение товаров на страничке не сеткой а списком.''')
    available = models.BooleanField(default=True, verbose_name='Доступен', help_text='''Это поле варьируется автоматически,
    если остаток больше 0 то оно активно, в случае если равно 0, доступность снимается. Поле нужно для 
    правильной фильтрафии товаров''')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен', blank=True)
    uploaded = models.DateTimeField(auto_now=True, verbose_name='Изменен', blank=True)

    special_offer = models.BooleanField(default=False, verbose_name='Спецпрелдожение', help_text='''
    При активации данного поля товар дополнительно попадает в список " спецпредложений ", которые отображются в бургере,
     из основной категории он не пропадает конечно же.''')
    review = models.JSONField(verbose_name='Отзывы на товар', default=dict)
    rate = models.IntegerField(verbose_name='Суммарный рейтинг', default=0)
    notify_list = models.JSONField(verbose_name='Список уведомлений', default=dict,
                                   help_text='Тут заносятся email пользователей, которых'
                                             ' нужно уведомить о поступлении товара. '
                                             'Это просходит автоматически.')  # {user_mail: 'null'}

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug, 'id': self.category.id})

    def save(self, *args, **kwargs):

        if self.old_price:
            self.special_offer = True

        if self.quantity > 0:
            self.available = True
        else:
            self.available = False

        super().save(*args, **kwargs)

        image = Image.open(self.photo.path)
        name = os.path.split(self.photo.path)[1].split('.')[0]

        if name != 'default_prod_black':
            if image.height > 400 or image.width > 400:
                resize = (400, 400)
                image.thumbnail(resize)

                image.save(self.photo.path)
                super().save()
            else:
                image.save(self.photo.path)
                super().save()

        all_reviews = self.review
        all_rate = []
        finel_rate = 0

        if len(all_reviews) < 100:
            for key in reversed(all_reviews):
                rate = all_reviews[key].keys()
                for b in rate:
                    all_rate.append(int(b))
        else:
            for i in range(0, 101):
                reversed_review_list = list(reversed(all_reviews.items()))
                rate = int(reversed_review_list[i][1][0])
                for b in rate:
                    all_rate.append(int(b))
        if len(all_rate) > 0:
            finel_rate = sum(all_rate) / len(all_rate)

        self.rate = finel_rate
        super().save(*args, **kwargs)

        if self.quantity > 0 and len(self.notify_list) > 0:
            list_email = []
            # current_site = Site.objects.get_current()

            for email in self.notify_list.keys():
                list_email.append(email)

            # Ссылка
            # на
            # товар
            # {current_site.domain}
            # {self.category.slug} / {lower(self.title)}
            send_mail(
                f'Уведомление о наличии товара {self.title}',
                f'''Товар {self.title} появился в наличии в количестве {self.quantity} шт. и доступен к покупке. ChasDetal.
                ''',
                'chasdetal@gmail.com',
                list_email
            )

            self.notify_list = {}
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']
        index_together = (('id', 'slug'),)


TYPE_BANNER = [
    ('SLIDER', 'Разместить в слайдере'),
    ('FIXED_POST', 'Разместить в фиксированном посте (можно только 1)'),
]


def image_folder_slider(instance, filename):
    now = datetime.datetime.now()
    return f'backgrounds/{str(now.year)}/{str(now.month)}/{str(now.day)}/{uuid.uuid4().hex}.webp'


class SliderBanner(models.Model):
    link = models.CharField(max_length=250, default='#', verbose_name='Ссылка',
                            help_text='''Ссылка которая при клике будет куда то уводить пользователя''')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано',
                                       help_text='''добавить/снять с публикации в слайдере. В случае слайдера, опубликовано может быть сразу несколько записей.
                                       В случае фиксированного поста, публиковаться будет только 1, даже если отметка "Опубликовано" стоит на нескольких.''')
    photo = WEBPField(upload_to=image_folder_slider, blank=True, help_text='''Для большого слайдера размер 966*400 (цвет фона страницы #f3efef) 
    . Для маленького банера размер 272*400. Для лучшего отображения в слайдере следует собирать картинки указанных рамзмеров.''')

    type_post = models.CharField(choices=TYPE_BANNER, default='SLIDER', max_length=25,
                                 verbose_name='Где расположить объявление')

    def save(self, *args, **kwargs):
        super().save()

        image = Image.open(self.photo.path)
        width = 0
        height = 0
        if self.type_post == 'SLIDER':
            width = 966
            height = 400
        elif self.type_post == 'FIXED_POST':
            width = 272
            height = 400

        if image.height > width or image.width > height:
            resize = (966, 400)
            image.thumbnail(resize)

            image.save(self.photo.path)
            super().save()
        else:
            image.save(self.photo.path)
            super().save()

    def __str__(self):
        return self.link

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеров/ы'


class Question(models.Model):
    question = models.CharField(max_length=250, verbose_name='Вопрос')

    answer = models.TextField(verbose_name='Ответ')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fio = models.CharField(max_length=250, verbose_name='Ф.И.О.', blank=True)
    wholesale = models.BooleanField(default=False, verbose_name='Оптовик')
    phone = PhoneNumberField(null=True, verbose_name='номер телефона')
    email = models.EmailField(max_length=250, verbose_name='электронная почта', blank=True)
    cdek_address = models.CharField(max_length=250, verbose_name='Адрес пункта выдачи сдек', blank=True)
    pochta_address = models.CharField(max_length=250, verbose_name='Адрес для доставки на Почту России', blank=True)
    email_verify = models.BooleanField(default=False, verbose_name='Подтверждение почты')
    purchased = models.JSONField(verbose_name='Купленные товары', default=dict,
                                 blank=True)  # {product_id:{user_id:{rate:review}}}
    total_sum = models.IntegerField(default=0, verbose_name='Общая сумма заказов за все время')
    total_orders = models.IntegerField(default=0, verbose_name='Общее количество заказов')
    last_date_order = models.DateTimeField(default=None, verbose_name='Дата последнего заказа', null=True)

    def __str__(self):
        return f'Профиль пользователя "{self.user.username} - оптовик: {self.wholesale} - {self.phone}"'

    def delete(self, using=None, keep_parents=False):
        product_reviews = self.purchased

        # Удаление отзыва на всех товарах при удалении профиля пользователя
        if len(product_reviews) > 0:
            for prod_id in product_reviews.keys():
                product = Product.objects.get(id=int(prod_id))
                prod_review = product.review
                if str(self.id) in prod_review:
                    prod_review.pop(str(self.id))

                product.review = prod_review
                product.save()

        super().delete()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Price(models.Model):
    sdek_delivery_price = models.DecimalField(verbose_name='Доставка "сдек"', max_digits=10, decimal_places=2)
    poshta_delivery_price = models.DecimalField(verbose_name='Доставка "почта"', max_digits=10, decimal_places=2)
    min_sum_for_wholesale = models.DecimalField(verbose_name='Минимальная цена для оптовика', max_digits=10,
                                                decimal_places=2)

    def __str__(self):
        return f'Профиль цен'

    class Meta:
        verbose_name = 'Цена (Доставка и Мин. сумма для оптовика)'
        verbose_name_plural = 'Цены (Доставка и Мин. сумма для оптовика)'


# Тут нужно будет написать логику которая будет просматривать, если есть true на send то
# - проверить есть ли true на send_has_done
# - если есть, то ничего попытаться отправить, если нет то попытаться отправить сообщение повторно, если ничего нет, то ничего не делать
# - при этом поля мессенж текст и поле трек номера не должны быть пусты
TYPE_OF_DELIVERY = [
    ('CDEK', 'СДЭК'),
    ('POCHTA', 'Почта РФ'),
]

STATUS_OF_ORDER = [
    ('MANUAL', 'Сообщение с оповещением отправлено о заказе'),
    ('INVOICE', 'Сообщение с реквизитами отправлено'),
    ('PAYMENT', 'Сообщение с оповещением об оплате отправлено'),
    ('TRACK', 'Сообщение с треком отправлены'),
    ('CLOSE', 'Заказ закрыт'),
    ('CANCEL', 'Заказ отменен'),
]


class Order(models.Model):
    order_num = models.IntegerField(verbose_name='Номер заказа', default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    type_delivery = models.CharField(choices=TYPE_OF_DELIVERY, default='POCHTA', max_length=25,
                                     verbose_name='тип доставки')
    status_order = models.CharField(choices=STATUS_OF_ORDER, default='MANUAL', max_length=50,
                                    verbose_name='статус заказа')
    address = models.CharField(max_length=250, default='none', verbose_name='адрес')
    email = models.EmailField(max_length=250, verbose_name='электронная почта', default='none')
    phone = PhoneNumberField(null=True, verbose_name='номер телефона')
    cart = models.TextField(max_length=250, verbose_name='заказ', default='none')
    discount = models.IntegerField(verbose_name='скидка', default=0)
    total_sum = models.IntegerField(verbose_name='общая сумма', default=0)
    track_number = models.CharField(max_length=100, verbose_name='трек номер посылки', default='none')
    send = models.BooleanField(default=False, verbose_name='отправить сообщение с реквизитами', help_text='''Укажи трек номер, поставь галку "отправить" 
        и нажми "сохранить". Тогда автоматически сообщение будет отправлено пользователю на номер телефона и почту с указанием трек номера.''')
    send_first = models.BooleanField(default=False, verbose_name='отправить сообщение с подтверждением оплаты',
                                     help_text='''Отправит сообщение с данными для перевода.''')
    send_second = models.BooleanField(default=False, verbose_name='отправить сообщение с данными доставки',
                                      help_text='''Отправит сообщение с подтверждением оплаты.''')
    close = models.BooleanField(default=False, verbose_name='отменить заказ', help_text='''Отметить галку и нажми "сохранить" 
    и тогда заказ будет закрыт а товары которые в нем числятся уйдут обратно в продажу.''')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return str(self.order_num)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.order_num == 0:
            self.order_num = self.id
        else:
            pass

        super().save(*args, **kwargs)

        messages_text = OrderText.objects.all().first()

        first_message = messages_text.details.replace('$', str(self.total_sum))
        second_message = messages_text.paid_for.replace('$', str(self.total_sum))
        second_message = second_message.replace('&', str(self.order_num))
        title_message = messages_text.title

        # При установке флагов в админ панели отправляют определенные сообщения пользователю
        if self.send and self.status_order == 'MANUAL':
            sendEmailAndSms(user_message_title=title_message,
                            user_message_text=first_message,
                            user_message_email=self.email,
                            phone=self.phone
                            )
            self.status_order = 'INVOICE'
            super().save(*args, **kwargs)
            # Отправляю сообщение с реквизитами и ставлю статус INVOICE
        elif self.send_first and self.status_order == 'INVOICE':
            sendEmailAndSms(user_message_title=title_message,
                            user_message_text=second_message,
                            user_message_email=self.email,
                            phone=self.phone
                            )
            self.status_order = 'PAYMENT'
            profile = Profile.objects.get(email=self.email)
            profile.total_orders = profile.total_orders + 1
            total_sum = profile.total_sum + self.total_sum
            profile.total_sum = total_sum
            profile.last_date_order = self.created

            profile.save()
            super().save(*args, **kwargs)
            # Отправляю сообщение с оповещением об оплате и ставлю статус PAYMENT
        elif self.send_second and self.status_order == 'PAYMENT':

            self.status_order = 'TRACK'

            if self.type_delivery == 'CDEK':
                type_delivery_for_mess = 'CDEK'
            elif self.type_delivery == 'POCHTA':
                type_delivery_for_mess = 'Почта России'
            third_message = messages_text.sent_by.replace('%', type_delivery_for_mess)
            third_message = third_message.replace('@', self.track_number)

            sendEmailAndSms(user_message_title=title_message,
                            user_message_text=third_message,
                            user_message_email=self.email,
                            phone=self.phone
                            )

            super().save(*args, **kwargs)
            # Сообщение с трек номером и статус TRACK. так же нужно брать из инпута сам трек

        if self.close:
            products = Product.objects.all()
            order_cart = self.cart.split('\n')
            order_cart_list = {}
            for i in order_cart:
                if len(i) > 0:
                    i = i.split('х')
                    quan = i[1].split(' ')

                    # В модель заказа может упасть такая запись
                    # Товар х 38 шт--35
                    # где --35 является фактическим.
                    # Если в момент заказа, каким то чудом вдруг фактический остаток меньше количества которое указал покупатель
                    # то в записи это укажется таким образом. 38 количество которое заказано (если заказано значит в момент оформления
                    # столько было) а 35 сколько доступно
                    #
                    # Логика ниже соответственно учитывает это и в случае отмены заказа, возвращает на продажу не 38 а 35
                    if '--' in quan[2]:
                        insertion_value = int(quan[2].split('--')[1])
                    else:
                        insertion_value = int(quan[1])

                    order_cart_list[i[0].replace(' ', '')] = insertion_value

            for i in products:
                if i.title in order_cart_list.keys():
                    one_prod = products.get(title=i.title)
                    one_prod.quantity += order_cart_list[i.title]
                    one_prod.save()

            self.cart = 'none'
            self.status_order = 'CANCEL'
            super().save(*args, **kwargs)


TYPE_OF_PROMOS = [
    ('DISCOUNT', 'Скидка'),
    ('BUYER_TYPE', 'Выдача статуса оптового покупателя'),
]


class Promocode(models.Model):
    description = models.TextField(blank=True, verbose_name='Описание')
    promo = models.CharField(max_length=50, unique=True, verbose_name='Промокод')
    type_of_promo = models.CharField(choices=TYPE_OF_PROMOS, default='DISCOUNT', max_length=25,
                                     verbose_name='тип промокода')
    discount = models.IntegerField(verbose_name='Скидка в %', default=0, blank=True, null=True, help_text='''Поле для промокода 
    скидок, обязательно только для промокодов дающие скидку на корзину. Значение которое будет установлено это процент,
     который скинется пользувателю в общей суммы.''')

    def __str__(self):
        return self.promo

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды/ов'


class Contact(models.Model):
    work_time = models.TextField(blank=True, verbose_name='График работы')
    phone = models.CharField(max_length=250, unique=True, verbose_name='Номер телефона для представления на сайте')
    phone_code = models.BigIntegerField(unique=True,
                                     verbose_name='Номер телефона для кода', help_text='Указывается без пробелов и спецсимволов. Подставляется в код для поддержки интерактивности')
    email = models.CharField(max_length=250, unique=True, verbose_name='Почта')
    email_feedback = models.EmailField(max_length=250, unique=False, verbose_name='Почта для формы обратной связи')
    address = models.CharField(max_length=250, unique=True, verbose_name='Адресс')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Контактная информация'
        verbose_name_plural = 'Контактная информация'


class Social(models.Model):
    vk = models.CharField(max_length=240, unique=True, verbose_name='ссылка на вконтакте', default='#')
    odnoklassniki = models.CharField(max_length=240, unique=True, verbose_name='ссылка на одноклассники', default='#')

    class Meta:
        verbose_name = 'Социалки'
        verbose_name_plural = 'Социалки'


class OrderText(models.Model):
    first_info = models.TextField(verbose_name='Первое сообщение после оформления заказа', help_text='''Первое сообщение которое будет выслано пользователю сразу после
    оформления им заказа. В этом поле нужно будет указать место установки номера заказа, этот номер будет подставляться автоматически. Достаточно 
    указать символ & в месте, где нужно указать номер заказа''', default='&')
    details = models.TextField(verbose_name='Сообщение к реквизитами для оплаты', help_text='''Указание реквизитов для оплаты. В этом поле нужно будет указать место для подстановки 
    суммы заказа, она встанет автоматически, достаточно только указать место для подставноки символом $''', default='$')
    paid_for = models.TextField(verbose_name='Подтверждение оплаченого заказа', help_text='''Что то вроде "заказ оплачен, ожидает отправки. Нужно указать место подстановки номера заказа 
    и суммы заказа с помощью символов & и $ соответственно"''', default='& - $')
    sent_by = models.TextField(verbose_name='Последнее сообщение с данными отправки', help_text='''Сообщение об отправке с трек номером. Для указания трек номера в каком
      либо месте сообщшения достаточно указать @, а для указания службы доставки указать знак % .
      Например "Товар отправле службой % . Трек номер отправления @""''', default='%')
    title = models.CharField(max_length=100,
                             verbose_name='Тема письма которая указывается при отправке письма покупателю',
                             default='none')
    email = models.EmailField(max_length=50, verbose_name='Почта на которую будет приходить уведомление о заказах',
                              default='none')

    # email_server = models.EmailField(max_length=50, verbose_name='Это почта сервера, которая указывается как "отправитель" в рассылках.',
    #                           default='none', help_text='Данные поле не стоит трогать если на самом сервере, в настройка не изменены сообветствующие настройки')

    def __str__(self):
        return self.first_info

    class Meta:
        verbose_name = 'Инструкция для покупателя'
        verbose_name_plural = 'Инструкция для покупателя'
