from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, ParticipantViewSet, MissionViewSet

router = DefaultRouter()
router.register('hostels', HostelViewSet, basename='hostel')
router.register('participants', ParticipantViewSet, basename='participant')
router.register('missions', MissionViewSet, basename='mission')

urlpatterns = router.urls