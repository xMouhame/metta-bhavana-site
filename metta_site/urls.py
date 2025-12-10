from django.contrib import admin
from django.urls import path
from main import views

# Add these ↓↓↓
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('appointments/', views.appointments, name='appointments'),
    path('contact/', views.contact, name='contact'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
