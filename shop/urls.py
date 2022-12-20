import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import settings
from django.conf.urls.static import static
from django.contrib.auth import views as authViews




urlpatterns = [
    path('admin/', admin.site.urls),
    path('pass-reset/', authViews.PasswordResetView.as_view(template_name='users/pass-reset.html'), name='pass-reset'),
    path('password_reset_complete/',
         authViews.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password_reset_confirm/<uidb64>/<token>/',
         authViews.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset_done/',
         authViews.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('', include('mainstoreapp.urls')),
    path('', include('users.urls')),
    path('card/', include('cart.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('captcha/', include('captcha.urls')),
    path('/__debug__/', include(debug_toolbar.urls)),


]


if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)