from django.urls import path, include

from . import views
from . import sync_with_external_db as sync

sync_urls = [
    path('users', sync.syncUsers),
    path('discount-cards', sync.syncDiscountCards),
    path('products', sync.syncProducts),
    path('brands', sync.syncBrands),
    path('categories', sync.syncCategories),
    path('images', sync.syncImages),
    path('colors', sync.syncColors),
    path('sizes-page', sync.syncSizesPage),
    path('current-season-collection', sync.syncCurrentSeasonCollection),
]

urlpatterns = [
    path('brands', views.BrandsView.as_view()),
    path('categories', views.CategoryListView.as_view()),
    path('products', views.ProductListView.as_view()),
    path('products/<str:productId>', views.ProductDetailView.as_view()),
    path('favorites', views.FavoritesView.as_view()),
    path('basket', views.BasketView.as_view()),
    path('check-promocode', views.checkPromocode),
    path('create-order', views.createOrder),
    path('check-order-status', views.checkOrderStatus),
    path('update-all-order-statuses', views.updateAllOwnOrdersStatus),
    path('main-content', views.MainContentView),
    path('discount-card-info', views.DiscountCardInfoView.as_view()),
    path('sizes-page', views.SizesPageView.as_view()),
    path('login', views.LoginView),
    path('might-be-interested', views.MightBeInterestedView.as_view()),
    path('registry-send-code', views.RegistrySendCodeView),
    path('registry-resend-code', views.RegistryResendCodeView),
    path('personal-info', views.PersonalInfoView.as_view()),
    path('change-password', views.ChangePasswordView),
    path('recovery-password-send', views.RecoveryPasswordSendView),
    path('recovery-password-check', views.RecoveryPasswordCheckView),
    path('recovery-password-complete', views.RecoveryPasswordCompleteView),
    path('sync/', include(sync_urls)),
    path('info/<str:infoName>', views.HelpfulInfoView.as_view()),
    path('subcategories-bind-random-product',
         views.subcategoriesBindRandomProduct),
    path('brands-gender-separate', views.brandsGenderSeparate),
]
