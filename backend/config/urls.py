from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def root_status(request):
    return JsonResponse({
        "status": "ok",
        "message": "AC backend is running. See /admin/ or /api/ for endpoints.",
    })


urlpatterns = [
    path('', root_status),
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/', include('products.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/wishlist/', include('wishlist.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/sellers/', include('sellers.urls')),
    path('api/support/', include('support.urls')),
    path('api/reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)