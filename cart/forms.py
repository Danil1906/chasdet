from django import forms
from phonenumber_field.formfields import PhoneNumberField


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(label='Количество', min_value=1, required=True,
                                  widget=forms.NumberInput(attrs={'class': 'form-control quantity-input',
                                                                  'min': '1',
                                                                  'name': 'value-changer',
                                                                  'type': 'number',
                                                                  'value': 0
                                                                  }))
    update = forms.BooleanField(required=False, initial=False,
                                widget=forms.HiddenInput(attrs={'id': 'quantity-update'}))


class CountryIndex(forms.Form):
    index = forms.IntegerField(label='Индекс города', required=True,
                               widget=forms.NumberInput(attrs={'class': 'form-control',
                                                               'style': 'width: 50%',
                                                               'id': 'index-input'}))


class DeliveryForm(forms.Form):
    index = forms.IntegerField(label='Индекс', widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'id': 'index-delivery'
    }))
    region = forms.CharField(label='Регион', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                          'id': 'region-delivery'}))
    city = forms.CharField(label='Город', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                       'id': 'city-delivery'}))
    street = forms.CharField(label='Улица', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                         'id': 'street-delivery'}))

    full_name = forms.CharField(label='Ф.И.О.', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                             'id': 'full-name-delivery'}))

    email = forms.EmailField(label='Email', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                         'id': 'email-delivery'}))

    name_delivery = forms.CharField(label='Вид доставики', required=True,
                                    widget=forms.HiddenInput(attrs={'id': 'delivery-name'}))


class DeliveryPhoneForm(forms.Form):
    phone = PhoneNumberField(widget=forms.NumberInput(attrs={'placeholder': 'Номер телефона',
                                                             'class': 'form-control',
                                                             'id': 'phone-delivery',
                                                             'min': 1}),

                             label="Номер телефона", required=True)
