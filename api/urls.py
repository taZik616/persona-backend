from django.urls import path, include

from . import views
from . import sync_with_external_db as sync

sync_urls = [
    path('users', sync.syncUsers),
    path('products', sync.syncProducts),
    path('brands', sync.syncBrands),
    path('categories', sync.syncCategories),
    path('images', sync.syncImages),
    path('colors', sync.syncColors),
    path('sizes-page', sync.syncSizesPage),
]

urlpatterns = [
    path('brands', views.BrandsView.as_view()),
    path('categories', views.CategoryListView.as_view()),
    path('products', views.ProductListView.as_view()),
    path('products/<str:productId>', views.ProductDetailView.as_view()),
    path('favorites', views.FavoritesView.as_view()),
    path('basket', views.BasketView.as_view()),
    path('main-content', views.MainContentView),
    path('sizes-page', views.SizesPageView.as_view()),
    path('login', views.LoginView),
    path('registry-send-code', views.RegistrySendCodeView),
    path('registry-resend-code', views.RegistryResendCodeView),
    path('personal-info', views.PersonalInfoView.as_view()),
    path('change-password', views.ChangePasswordView),
    path('recovery-password-send', views.RecoveryPasswordSendView),
    path('recovery-password-confirm', views.RecoveryPasswordConfirmView),
    path('sync/', include(sync_urls)),
    path('info/<str:infoName>', views.HelpfulInfoView.as_view()),
    path('subcategories-bind-random-product',
         views.subcategoriesBindRandomProduct)
]
