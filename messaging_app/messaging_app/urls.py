from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include the chat app routes under /api/
    path('api/', include('chats.urls')),

    # Optional: browsable API login/logout
    path('api-auth/', include('rest_framework.urls')),
]
