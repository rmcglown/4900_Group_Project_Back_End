

"""
URL configuration for bookshelf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from api import views
from api.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth', include('rest_framework.urls')),
    path('api/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', views.book_list),
    path('api/books/', views.book_list),
    path('api/books/<int:pk>/', views.getBook),
    path(r'api/checkout/<int:copy_id>/', views.checkout_book),
    path('api/loans/<int:loan_id>/pay_fine/', views.pay_fine, name='pay_fine'),
    path('api/my-fines/', views.my_fines, name='my_fines'),
    path('api/loans/mine/', views.my_loans, name='my_loans'),

    path('api/books/<int:book_id>/copies/', views.book_copies),
    path('register/', RegisterView.as_view(), name='auth_register'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), #serve media files when deployed
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}), #serve static files when deployed
]
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root =settings.STATIC_ROOT)
else:
    urlpatterns += re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    urlpatterns += re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),


