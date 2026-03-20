from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('voice/', include('voice_assistant.urls')),
    path('', include('academics.urls')),
    path('results/', include('results.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
