from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin


# Register your models here.
class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(label='Категория', widget=CKEditorUploadingWidget())

    class Meta:
        model = Product
        fields = '__all__'


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    form = ProductAdminForm
    save_on_top = True
    list_display = ('id', 'title', 'slug', 'get_description', 'category', 'quantity', 'price', 'old_price',
                    'available', 'is_published', 'special_offer', 'get_photo', 'created', 'uploaded', 'glass')
    list_display_links = ('id', 'title',)
    search_fields = ('title',)
    list_filter = ('category',)
    readonly_fields = ('created', 'get_photo', 'uploaded', 'review', 'rate', 'available', 'notify_list')
    fields = ('title', 'slug', 'description', 'category', 'quantity', 'price', 'old_price', 'wholesale_price',
              'available', 'is_published', 'special_offer', 'photo', 'get_photo', 'review',
              'rate', 'notify_list', 'created', 'uploaded', 'glass')

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="60">')
        return '-'

    def get_description(self, obj):
        if obj.description:
            if len(obj.description) > 100:
                return obj.description[:100]
            return obj.description

    get_description.short_description = "Description"

    get_photo.short_description = 'фото'


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sdek_delivery_price', 'poshta_delivery_price', 'min_sum_for_wholesale')
    list_display_links = ('id', 'sdek_delivery_price', 'poshta_delivery_price', 'min_sum_for_wholesale')


class ProfileAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'user', 'fio', 'phone', 'wholesale', 'total_sum', 'total_orders', 'last_date_order', 'email_verify')
    list_display_links = ('id', 'user', 'fio')
    search_fields = ('user', 'fio', 'phone', 'email')
    readonly_fields = ('email_verify', 'total_sum', 'total_orders', 'last_date_order')
    list_filter = ('last_date_order', 'total_sum', 'total_orders', 'email_verify')
    fields = (
    'user', 'fio', 'phone', 'wholesale', 'email', 'total_sum', 'total_orders', 'last_date_order', 'cdek_address', 'pochta_address', 'email_verify')


class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'promo', 'description', 'type_of_promo', 'discount')
    list_display_links = ('id', 'promo')


class SliderAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'link', 'type_post', 'get_photo', 'is_published')
    list_display_links = ('id', 'link',)
    search_fields = ('link', 'type_post')
    list_filter = ('type_post',)
    fields = ('link', 'type_post', 'photo', 'is_published')

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="60">')
        return '-'

    get_photo.short_description = 'фото'


class QuestionAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'question', 'answer')
    list_display_links = ('id', 'question', 'answer')
    search_fields = ('question', 'answer')
    list_filter = ('question',)
    fields = ('question', 'answer')


class OrderTextAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'first_info', 'details', 'paid_for', 'sent_by', 'email', 'title')
    list_display_links = ('id', 'first_info', 'details', 'paid_for', 'sent_by', 'email')
    fields = ('first_info', 'details', 'paid_for', 'sent_by', 'email', 'title')


class OrderAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
    'id', 'order_num', 'total_sum', 'email', 'phone', 'address', 'created', 'track_number', 'status_order', 'close')
    list_display_links = ('id', 'order_num', 'email', 'phone')
    search_fields = ('id', 'order_num', 'address', 'email', 'phone', 'track_number', 'total_sum')
    list_filter = ('email', 'phone', 'created', 'status_order', 'address', 'close')
    readonly_fields = (
        'order_num', 'type_delivery', 'discount', 'total_sum', 'cart', 'address', 'email', 'phone', 'status_order',
        'created')
    fields = (
        'created', 'order_num', 'cart', 'discount', 'total_sum', 'type_delivery', 'address', 'email', 'phone',
        'status_order', 'send', 'send_first', 'track_number', 'send_second', 'close')


class PrivacyPolicyForm(forms.ModelForm):
    text = forms.CharField(label='Текст', widget=CKEditorUploadingWidget())

    class Meta:
        model = PrivacyPolicy
        fields = '__all__'


class PrivacyPolicyAdmin(admin.ModelAdmin):
    form = PrivacyPolicyForm
    list_display = ('text',)
    list_display_links = ('text',)
    fields = ('text',)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('work_time', 'phone',  'email', 'address')
    list_display_links = ('work_time', 'phone', 'email', 'address')
    fields = ('work_time', 'phone', 'email', 'phone_code', 'email_feedback', 'address')


class SocialAdmin(admin.ModelAdmin):
    list_display = ('id', 'vk', 'odnoklassniki')
    list_display_links = ('id', 'vk', 'odnoklassniki')
    fields = ('vk', 'odnoklassniki')


admin.site.register(
    Category,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
        # ...more fields if you feel like it...
    ),
    list_display_links=(
        'indented_title',
    ),
    prepopulated_fields={"slug": ('title',)},
)
admin.site.register(Product, ProductAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(SliderBanner, SliderAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(OrderText, OrderTextAdmin)
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
admin.site.register(Social, SocialAdmin)
admin.site.register(Contact, ContactAdmin)

AdminSite.site_title = 'Администрирование Час - Деталь'
AdminSite.site_header = 'Администрирование Час - Деталь'
