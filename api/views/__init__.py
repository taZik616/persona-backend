from .brands import BrandsView
from .login import LoginView
from .registry_send_code import RegistrySendCodeView, RegistryResendCodeView
from .personal_info import PersonalInfoView
from .change_password import ChangePasswordView
from .recovery_password import RecoveryPasswordCheckView, RecoveryPasswordCompleteView, RecoveryPasswordSendView
from .product import ProductListView, ProductDetailView
from .subcategories_bind_random_product import subcategoriesBindRandomProduct
from .categories import CategoryListView
from .favorites import FavoritesView
from .basket import BasketView
from .helpful_info import HelpfulInfoView
from .main_content import MainContentView
from .sizes_page import SizesPageView
from .might_be_interested import MightBeInterestedView
from .brands_gender_separate import brandsGenderSeparate
from .discount_card_info import DiscountCardInfoView
from .check_promocode import checkPromocodeView
from .create_order import createOrder
from .create_fast_order import createFastOrder
from .check_order_status import checkOrderStatus, updateAllOwnOrdersStatus
from .order_personal_discount_calc import orderPersonalDiscountCalcView
from .delivery_price import deliveryPrice
from .orders import getOwnOrders
from .gift_cards import getOwnMintedGiftCards, updateAllOwnGiftCardStatuses, getGiftCardTypes, mintGiftCard
