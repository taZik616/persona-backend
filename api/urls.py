from django.urls import path, include

from . import views

from rest_framework import routers
from . import sync_with_external_db as sync

router = routers.SimpleRouter()
# router.register(r'brands', views.BrandsView)

sync_urls = [
    path('users', sync.synсUsers),
]

urlpatterns = [
    path('', include(router.urls)),
    path('brands', views.BrandsView.as_view()),
    path('login', views.LoginView),
    path('registry-send-code', views.RegistrySendCodeView),
    path('sync/', include(sync_urls)),
]
