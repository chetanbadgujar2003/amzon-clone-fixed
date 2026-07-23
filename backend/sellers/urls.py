from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.SellerRegisterView.as_view(), name='seller-register'),
    path('login/', views.SellerLoginView.as_view(), name='seller-login'),
    path('me/', views.SellerMeView.as_view(), name='seller-me'),
    path('me/products/', views.SellerMeProductsView.as_view(), name='seller-me-products'),
    path('me/products/<int:product_id>/', views.SellerMeProductDetailView.as_view(), name='seller-me-product-detail'),

    # admin-only
    path('admin/', views.AdminSellerListView.as_view(), name='admin-seller-list'),
    path('admin/<int:seller_id>/verify/', views.AdminSellerVerifyView.as_view(), name='admin-seller-verify'),
    path('admin/<int:seller_id>/reject/', views.AdminSellerRejectView.as_view(), name='admin-seller-reject'),
    path('admin/<int:seller_id>/flag/', views.AdminSellerFlagView.as_view(), name='admin-seller-flag'),
    path('admin/<int:seller_id>/unflag/', views.AdminSellerUnflagView.as_view(), name='admin-seller-unflag'),
    path('admin/<int:seller_id>/', views.AdminSellerDetailView.as_view(), name='admin-seller-detail'),
    path('admin/<int:seller_id>/products/', views.AdminSellerProductsView.as_view(), name='admin-seller-products'),
]
