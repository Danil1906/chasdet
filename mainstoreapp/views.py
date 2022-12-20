from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from cart.cart import Cart
from .models import *
from cart.forms import CartAddProductForm
from django.core.mail import send_mail
from .forms import ContactForm, ProfileUpdate, UserUpdate, ReviewFrom
from django.contrib import messages
from django.core.cache import cache


class HomeView(ListView):
    model = Category
    template_name = 'mainstoreapp/index.html'
    context_object_name = 'categories'

    def get_queryset(self):
        category_home = cache.get('category_home')
        if not category_home:
            category_home = Category.objects.all().select_related('parent')
            cache.set('category_home', category_home, 60 * 60)

        category_home = Category.objects.all().select_related('parent')

        return category_home

    def get_context_data(self, *, object_list=None, **kwargs):
        slider_objs = cache.get('slider_objs')
        if not slider_objs:
            slider_objs = SliderBanner.objects.all()
            cache.set('slider_objs', slider_objs, 60 * 60)

        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Главная'

        ctx['slider_posts'] = slider_objs.filter(type_post='SLIDER', is_published=True)
        ctx['fixed_posts'] = slider_objs.filter(type_post='FIXED_POST', is_published=True).first()

        return ctx


class FaqView(ListView):
    model = Category
    template_name = 'mainstoreapp/faq.html'
    context_object_name = 'faq'

    def get_queryset(self):
        question_list = cache.get('question_list')
        if not question_list:
            question_list = Question.objects.all()
            cache.set('question_list', question_list, 60 * 120)

        return question_list

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Часто задаваемые вопросы'

        return ctx


class PrivacyPolicyClass(ListView):
    model = PrivacyPolicy
    template_name = 'mainstoreapp/privacy_policy.html'
    context_object_name = 'policy'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Политика конфиденциальности'

        ctx['text_policy'] = cache.get('text_policy')
        if not ctx['text_policy']:
            ctx['text_policy'] = PrivacyPolicy.objects.first()
            cache.set('text_policy', ctx['text_policy'], 60 * 180)

        return ctx


class DetailCategoryView(ListView):
    model = Category
    template_name = 'mainstoreapp/view_categories.html'
    context_object_name = 'cat_or_prod'
    paginate_by = 12
    allow_empty = True

    def get_queryset(self):
        # category = cache.get('category')
        # if not category:
        #     category = Category.objects.get(slug=self.kwargs['slug']).get_children()
        #     cache.set('category', category, 60 * 60)

        print(self.request)
        print(self.kwargs)
        category = Category.objects.get(id=self.kwargs['id']).get_children()
        cache.set('category', category, 60 * 60)

        if category:
            base = category
        else:
            base = Product.objects.filter(category=Category.objects.get(id=self.kwargs['id'])).select_related(
                'category').order_by('-available', 'title')
        return base

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['id'] = self.kwargs['id']
        ctx['cart_product_form'] = CartAddProductForm()
        ctx['request_bread'] = self.request
        ctx['request_bread'] = self.request

        if self.request.user.is_authenticated:
            ctx['profile'] = Profile.objects.filter(user=User.objects.get(username=self.request.user)).first()

        cart = Cart(self.request)
        items = None
        items_len = len(cart.keys)
        if items_len > 0:
            items = cart

        if ctx['cat_or_prod']:
            if isinstance(ctx['cat_or_prod'][0], Product):
                dict_of_prod = []

                for i in cart:
                    for b in ctx['cat_or_prod']:
                        if b.id == i['product'].id:
                            dict_of_prod.append([b.id, i['quantity']])

                ctx['items_cart'] = dict_of_prod

        return ctx

    def post(self, request, **kwargs):
        data = {}
        prod_id = self.kwargs['id']

        if self.request.user.is_authenticated:
            user_email = request.user.profile.email

            data = {'status': 'none'}
            product = Product.objects.filter(id=prod_id).first()
            product_list_notify = product.notify_list
            product_list_notify[user_email] = ''
            product.notify_list = product_list_notify
            product.save()
            data['status'] = 'auth'
            return JsonResponse(data)
        else:
            data['status'] = 'noauth'
            return JsonResponse(data)


class Search(ListView):
    template_name = 'mainstoreapp/search.html'
    context_object_name = 'products'
    paginate_by = 12
    allow_empty = True

    def get_queryset(self):
        return Product.objects.filter(title__icontains=self.request.GET.get('s')).select_related('category').order_by(
            '-available', 'title')

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['s'] = f"s={self.request.GET.get('s')}&"
        ctx['title'] = f"Поиск по '{self.request.GET.get('s')}'"
        ctx['cart_product_form'] = CartAddProductForm()
        if self.request.user.is_authenticated:
            ctx['profile'] = Profile.objects.filter(user=User.objects.get(username=self.request.user)).first()

        cart = Cart(self.request)
        dict_of_prod = []

        for i in cart:
            for b in ctx['products']:
                if b.id == i['product'].id:
                    dict_of_prod.append([b.id, i['quantity']])

        items = None
        items_len = len(cart.keys)
        if items_len > 0:
            items = cart

        ctx['items_cart'] = dict_of_prod

        return ctx


class SpecialOffers(ListView):
    model = Product
    template_name = 'mainstoreapp/special_offers_base.html'
    context_object_name = 'offers'
    paginate_by = 12
    allow_empty = True

    def get_queryset(self):
        return Product.objects.all().filter(special_offer=True, is_published=True).select_related('category')

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cart_product_form'] = CartAddProductForm()
        ctx['special_offers'] = True

        cart = Cart(self.request)
        items = None
        items_len = len(cart.keys)
        if items_len > 0:
            items = cart

        if ctx['offers']:
            if isinstance(ctx['offers'][0], Product):
                dict_of_prod = []
                for i in cart:
                    for b in ctx['offers']:
                        if b.id == i['product'].id:
                            dict_of_prod.append([b.id, i['quantity']])

                ctx['items_cart'] = dict_of_prod

        return ctx


class DetailProductView(ListView):
    model = Product
    context_object_name = 'cat_or_prod'
    template_name = 'mainstoreapp/view_product.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.kwargs['slug']
        ctx['product'] = Product.objects.get(slug=self.kwargs['slug'])
        ctx['id'] = self.kwargs['id']
        ctx['cart_product_form'] = CartAddProductForm()

        profiles = Profile.objects.all().select_related('user')
        if self.request.user.is_authenticated:
            user_profile = profiles.get(user=self.request.user)
            ctx['profile'] = user_profile

        cart = Cart(self.request)
        dict_of_prod = []

        for i in cart:
            if ctx['product'].id == i['product'].id:
                dict_of_prod.append([ctx['product'].id, i['quantity']])

        items = None
        items_len = len(cart.keys)
        if items_len > 0:
            items = cart

        ctx['items_cart'] = dict_of_prod

        ctx['rate'] = ctx['product'].rate

        # Определяю покупал ли пользовател данный товар, может ли он оставлять отзыв
        ctx['can_review'] = False
        if self.request.user.is_authenticated:
            product_id = ctx['product'].id
            print(product_id)
            user_purchased_dict = user_profile.purchased
            print(user_purchased_dict)
            if str(product_id) in user_purchased_dict.keys():
                ctx['can_review'] = True

        # Собираю отзывы
        all_reviews_list = {}
        review_dict = ctx['product'].review
        review_dict_keys = review_dict.keys()
        for key in review_dict_keys:
            user_review = profiles.get(id=key).user.username
            one_review_key = review_dict[key].keys()
            one_review = ''
            for i in one_review_key:
                all_reviews_list[user_review] = review_dict[key][i]

        ctx['product_reviews'] = all_reviews_list

        # Формирую форму
        if self.request.user.is_authenticated:
            content = ''
            user_id = str(user_profile.id)
            if user_id in review_dict.keys():
                user_review_dist = review_dict[user_id]
                key = user_review_dist.keys()

                for i in key:
                    content = user_review_dist[i]
                if len(content) > 1:
                    ctx['reference_btn'] = True
            ctx['review_form'] = ReviewFrom(initial={'content': content})
        else:
            ctx['review_form'] = ReviewFrom()

        return ctx


def contact_page(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        email_for_feedback = Contact.objects.all().first().email_feedback
        if form.is_valid():
            content = form.cleaned_data['content']
            email = form.cleaned_data['email']
            content += f' \n \n ОТПРАВИТЕЛЬ {email}'
            mail = send_mail(form.cleaned_data['subject'], content, 'chasdetal@gmail.com',
                             [email_for_feedback], fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('contact_page')
            else:
                messages.error(request, 'Ошибка, что то не так')
    else:
        form = ContactForm()
    return render(request, 'mainstoreapp/contact_page.html', {'form': form})


class ProfileEdit(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'mainstoreapp/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile_form'] = ProfileUpdate(instance=self.request.user.profile)
        ctx['user_form'] = UserUpdate()

        return ctx

    # Данные проходят, только вот при сохранении создается доп пользователь и доп профиль, пустые, вместо редактирования
    #     существующих
    def post(self, request, *args, **kwargs):
        profile_for = ProfileUpdate(self.request.POST, instance=self.request.user.profile)

        if profile_for.is_valid():
            profile_for.save()

            messages.success(self.request, 'Данные успешно обновлены')
            return redirect('profile')
        else:
            messages.error(self.request, 'Что то пошло не так')

        return redirect('profile')


# Method to update the password from the user profile page
@login_required
def pass_update_in_profile(request):
    if request.method == 'POST':
        user_form = UserUpdate(request.POST)
        if user_form.is_valid():
            form = user_form.cleaned_data
            new_pass = form['password1']
            user = request.user
            user_model = User.objects.get(username=user)
            user_model.set_password(new_pass)
            user_model.save()
            user_log = authenticate(request, username=user, password=new_pass)
            login(request, user_log)
            messages.success(request, 'Пароль успешно обновлен')
        else:
            messages.error(request, 'Что то пошло не так')

    return redirect('profile')


@login_required
def delivery_delete_in_profile(request, delivery):
    username = request.user.id
    user = get_object_or_404(Profile, user=username)
    if delivery == 1:
        user.pochta_address = ''
        user.save()
    elif delivery == 2:
        user.cdek_address = ''
        user.save()
    else:
        pass
    return redirect('profile')


def product_review(request, product_id):
    data = {}
    form = ReviewFrom(request.POST)
    profile = Profile.objects.get(user=request.user)
    profile_id = profile.id
    # {product_id: {rate: review}}
    product = Product.objects.get(id=product_id)
    # {user_id:{rate:review}}

    if form.is_valid():
        data = form.cleaned_data
        content = data['content']
        rate = data['rate_star']

        profile_reviews = profile.purchased
        profile_reviews[str(product_id)] = {rate: content}
        profile.save()

        product_reviews = product.review

        product_reviews[str(profile_id)] = {rate: content}
        product.save()

        messages.success(request,
                         'Отзыв успешно оставлен')
    else:
        messages.error(request,
                       'Ошибка. Что то прошло не так.')

    return JsonResponse(data)
