from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # All API endpoints are namespaced under /api/
    path('api/', include('chats.urls')),

    # Optional: enable DRF’s built-in login/logout for browsable API
    path('api-auth/', include('rest_framework.urls')),
]
