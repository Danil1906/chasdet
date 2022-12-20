from django import forms
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from phonenumber_field.formfields import PhoneNumberField

from mainstoreapp.models import Profile


class ContactForm(forms.Form):
    subject = forms.CharField(label='Тема', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Почта @', widget=forms.TextInput(attrs={'class': 'form-control',
                                                                            'placeholder': '''Почтовый адрес для получения ответа'''}))
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    captcha = CaptchaField()


class ProfileUpdate(forms.ModelForm):
    phone = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'Номер телефона',
                                                           'class': 'form-control',
                                                           'id': 'form-phone-field'}),

                             label="Номер телефона", required=False)

    cdek_address = forms.CharField(label='Адрес пункта выдачи CDEK', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly'
    }))

    pochta_address = forms.CharField(label='Адрес для Почты России', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly'
    }))

    class Meta:
        model = Profile
        fields = ['phone', 'cdek_address', 'pochta_address']


class UserUpdate(forms.ModelForm):
    password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['password1', 'password2']


class ReviewFrom(forms.Form):
    content = forms.CharField(label='Отзыв о товаре', widget=forms.Textarea(
        attrs={'name': 'textarea-review', 'class': 'form-control prod-card__review_input', 'rows': 5}))
    rate_star = forms.IntegerField(label='Рейтинг',
                                   widget=forms.HiddenInput(attrs={'class': 'rate-star__input-hidden'}))
