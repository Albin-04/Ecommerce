from django.urls import path
from my_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products', views.pro, name='pro'),
    path('add', views.add, name='add'),
    path('delete/<int:pro_id>/', views.delete_product, name='delete'),
    path('edit/<int:pro_id>/', views.edit, name='edit'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
     path('clear-cache/', views.clear_cache, name='clear_cache'),

    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Review URLs
    path('pro/<int:product_id>/', views.product_detail, name='product_detail'),
    path('pro/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('thank-you/', views.thank_you, name='thank_you'),
]



