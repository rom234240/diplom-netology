from django.urls import path
from .views import PartnerUpdate, RegisterView, LoginView, ProductListView


urlpatterns = [
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register', RegisterView.as_view(), name='user-register'),
    path('user/login', LoginView.as_view(), name='user-login'),
    path('products', ProductListView.as_view(), name='product-list'),
]