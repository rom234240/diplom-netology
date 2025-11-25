from django.urls import path
from .views import BasketDetailView, BasketView, ContactDetailView, ContactListView, PartnerUpdate, RegisterView, LoginView, ProductListView


urlpatterns = [
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register', RegisterView.as_view(), name='user-register'),
    path('user/login', LoginView.as_view(), name='user-login'),
    path('products', ProductListView.as_view(), name='product-list'),
    path('user/contact', ContactListView.as_view(), name='contact-list'),
    path('user/contact/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),
    path('basket', BasketView.as_view(), name='basket'),
    path('basket/<int:pk>', BasketDetailView.as_view(), name='basket-detail'),
]