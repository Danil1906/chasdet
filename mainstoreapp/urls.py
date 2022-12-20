from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('special_offers/', SpecialOffers.as_view(), name='offers'),
    path('privacy_policy/', PrivacyPolicyClass.as_view(), name='privacy_policy'),
    path('category/<str:slug>-<int:id>/', DetailCategoryView.as_view(), name='category'),
    path('category/<int:id>', DetailCategoryView.as_view(), name='product_notify'),
    path('product/review/<int:product_id>', product_review, name='product_review'),
    path('<int:id>/<slug:slug>/', DetailProductView.as_view(), name='product'),
    path('search/', Search.as_view(), name='search'),
    path('contact_page/', contact_page, name='contact_page'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('profile/', ProfileEdit.as_view(), name='profile'),
    path('profile/pass', pass_update_in_profile, name='profile-pass'),
    path('profile/<int:delivery>', delivery_delete_in_profile, name='profile-delivery'),

]


