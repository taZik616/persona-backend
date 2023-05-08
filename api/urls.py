from django.urls import path, include

from . import views

from rest_framework import routers

router = routers.SimpleRouter()
# router.register(r'brands', views.BrandsView)


urlpatterns = [
    path('', include(router.urls)),
    path('brands', views.BrandsView.as_view()),
    path('login', views.LoginView),
    path('registry-send-code', views.RegistrySendCodeView),
]
