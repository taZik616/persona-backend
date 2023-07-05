from .basket import BasketView
from .brands import BrandsView
from .brands_gender_separate import brandsGenderSeparate
from .categories import CategoryListView
from .change_password import ChangePasswordView
from .check_order_status import checkOrderStatus, updateAllOwnOrdersStatus
from .check_promocode import checkPromocodeView
from .create_fast_order import createFastOrder
from .create_order import createOrder
from .delivery_price import deliveryPrice
from .discount_card_info import DiscountCardInfoView
from .favorites import FavoritesView
from .gift_cards import (
    getGiftCardTypes,
    getOwnMintedGiftCards,
    mintGiftCard,
    updateAllOwnGiftCardStatuses,
)
from .helpful_info import getHelpfulInfo
from .login import LoginView
from .main_content import MainContentView
from .might_be_interested import MightBeInterestedView
from .order_personal_discount_calc import orderPersonalDiscountCalcView
from .orders import getOwnOrders
from .personal_info import PersonalInfoView
from .product import ProductDetailView, ProductListView
from .recovery_password import (
    RecoveryPasswordCheckView,
    RecoveryPasswordCompleteView,
    RecoveryPasswordSendView,
)
from .registry_send_code import RegistryResendCodeView, RegistrySendCodeView
from .sizes_page import SizesPageView
from .subcategories_bind_random_product import subcategoriesBindRandomProduct
