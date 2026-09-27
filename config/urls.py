from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from competition.views import HostelViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('competition.urls')),
    path('api/leaderboard/', HostelViewSet.as_view({'get': 'leaderboard'}), name='leaderboard'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api-auth/', include('rest_framework.urls')),
]