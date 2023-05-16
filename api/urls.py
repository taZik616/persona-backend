from django.urls import path, include

from . import views

from rest_framework import routers
from . import sync_with_external_db as sync

router = routers.SimpleRouter()
# router.register(r'brands', views.BrandsView)

sync_urls = [
    path('users', sync.syncUsers),
    path('products', sync.syncProducts),
    path('brands', sync.syncBrands),
    path('categories', sync.syncCategories),
    path('images', sync.syncImages),
]

urlpatterns = [
    path('', include(router.urls)),
    path('brands', views.BrandsView.as_view()),
    path('products', views.ProductListView.as_view()),
    path('login', views.LoginView),
    path('registry-send-code', views.RegistrySendCodeView),
    path('personal-info', views.PersonalInfoView.as_view()),
    path('change-password', views.ChangePasswordView),
    path('recovery-password-send', views.RecoveryPasswordSendView),
    path('recovery-password-confirm', views.RecoveryPasswordConfirmView),
    path('sync/', include(sync_urls)),
]
