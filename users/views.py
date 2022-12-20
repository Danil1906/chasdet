from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.views import View
from django.contrib.auth.models import User

from .forms import UserRegisterForm, UserLoginForm, PromoForm
from django.contrib.auth import login, logout, get_user_model, authenticate
from mainstoreapp.models import Profile, Promocode

# подтверждение почтовог адреса
User = get_user_model()


def check_verify_email(request, user, profile):
    username = user.username
    password = user.password

    data = {'none': 'none'}

    if username is not None and password:
        user_cache = authenticate(
            request,
            username=username,
            password=password,
        )
        if not profile.email_verify:
            send_email_verify(request, user)
            messages.error(request, 'Кажется почта не подтверждена. Проверьте свой почтовый ящик, возможно письмо '
                                    'угодило в спам')
            data['reload'] = 'true'
            return JsonResponse({'data': data})

        if user_cache is None:
            messages.error(request, 'Что то не так. Проверьте корректность заполненных данных и попробуйте снова')
            data['reload'] = 'true'
            return JsonResponse({'data': data})
        else:
            messages.error(request, 'Что то не так. Проверьте корректность заполненных данных и попробуйте снова')
            data['reload'] = 'true'
            return JsonResponse({'data': data})

    return JsonResponse({'data': data})


def send_email_verify(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    }

    message = render_to_string(
        'users/verify_email.html',
        context=context
    )
    email = EmailMessage(
        'регистрация ChasDetal',
        message,
        to=[user.email],
    )
    email.send()


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):

            profile = Profile.objects.get(user=user)
            profile.email_verify = True
            profile.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '''Ссылка по которой вы перешли более не корректна. 
            Попробуте залогиниться с указанными вами при регистрации данными.''')
            redirect('home')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user


def register(request, promo=True):
    promo = True

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        promo_form = PromoForm(request.POST)

        if form.is_valid():
            cf = form.cleaned_data
            name = cf['username']
            phone = cf['phone']
            email = cf['email']
            profiles = Profile.objects.all()

            have_this_data = profiles.filter(email=email).exists() or User.objects.filter(username=name).exists()
            re_registration = False

            if have_this_data:
                re_registration = Profile.objects.filter(email=email).first().email_verify

            if not have_this_data or not re_registration:
                user_form = form.save()

                # В момент создания профиля срабатывает сигнал который заводит профиль с переданными данными

                profile = Profile.objects.all().filter(user=User.objects.get(username=name)).first()
                profile.phone = phone
                profile.email = email

                user = User.objects.get(email=email)

                if Promocode.objects.filter(type_of_promo='BUYER_TYPE').exists():
                    promo = Promocode.objects.all().filter(type_of_promo='BUYER_TYPE').order_by('-id').first()
                    bd_code = promo.promo.upper().replace(' ', '')
                else:
                    bd_code = False
                    promo = False
                if promo_form.is_valid():
                    cf = promo_form.cleaned_data
                    code = cf['promo']
                    code = code.upper().replace(' ', '')

                    if promo and bd_code == code:
                        profile.wholesale = True
                        profile.save()
                        messages.success(request,
                                         f'''На адрес {email} было выслано письмо с ссылкой для подтверждения почтового адреса.
                                          Аккаунту автоматически будет присвоен статус "оптового покупателя"''')
                        send_email_verify(request, user)
                        return redirect('home')
                    elif code == '':
                        profile.save()
                        messages.success(request,
                                         f'''На адрес {email} было выслано письмо с ссылкой для подтверждения почтового адреса''')
                        send_email_verify(request, user)
                        return redirect('home')
                    else:
                        profile.save()
                        messages.error(request,
                                       f'''Промокод не применен, статус оптового покупателя не был присвоен, возможно ошибка в написании
                                          промокода или же промокод более не активен.
                                          Для продолжения регистарции аккаунта как "розничного покупателя" перейдите на почту {email} и подтвердите адрес.''')
                        send_email_verify(request, user)
                        return redirect('home')
            else:
                messages.error(request,
                               f'''На сайте уже зарегистрирован пользователь с таким email или логином''')
                return redirect('register')

            profile.save()

            login(request, user_form)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
        promo_form = PromoForm()
    if request.user.is_authenticated:
        profile = Profile.objects.all().filter(user=User.objects.get(username=request.user)).first()
    return render(request, 'users/register.html', {'title': 'Регистрация',
                                                   'form': form,
                                                   'promo': promo,
                                                   'promo_form': promo_form})


@login_required
def auth_promo(request):
    if request.method == 'POST':
        form = PromoForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            code = cf['promo']
            promo = Promocode.objects.all().filter(type_of_promo='BUYER_TYPE').first()
            profile = Profile.objects.all().filter(user=User.objects.get(username=request.user)).first()
            if promo.promo == code:
                profile.wholesale = True
                profile.save()
                messages.success(request,
                                 '''Вам был присвоен статус оптового покупателя, теперь для вас доступны оптовые цены 
                                 на товары, на которых такие цены распростряняются.''')
                return redirect('home')
            else:
                profile.save()
                messages.error(request,
                               '''Промокод не подошел. Возможно, он уже не активен. 
                               Попробуйте ввести его еще раз что бы убедиться что ошибка не в написании промокода.''')
                return redirect('auth_promo')

    else:
        form = PromoForm()

    return render(request, 'users/auth_promo.html', {'form': form})


def user_login(request):
    data = 'All Right'
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                return None
            else:
                profile = Profile.objects.get(user=user)
                if user.check_password(password):
                    if profile.email_verify:
                        login(request, user)
                    else:
                        print('Условие вышло')
                        check_verify_email(request, user, profile)
                else:
                    messages.error(request, 'Логин или пароль не указаны не верно.')
                    return JsonResponse({'data': data})

            return JsonResponse({'data': data})


def user_logout(request):
    logout(request)
    return redirect('home')
