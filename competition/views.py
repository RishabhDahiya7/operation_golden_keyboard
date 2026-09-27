from django.utils import timezone
from django.db.models import Sum, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hostel, Participant, Mission
from .serializers import (
    HostelSerializer, HostelDetailSerializer,
    ParticipantSerializer, MissionSerializer,
)
from .permissions import IsMissionOwnerOrReadOnly, IsStaffOrReadOnlyForCoreFields
from .throttles import ClaimMissionThrottle


def expire_overdue_missions():
    """Flip any mission whose deadline has passed to 'expired', unless already cracked."""
    Mission.objects.filter(
        deadline__lt=timezone.now()
    ).exclude(status__in=['cracked', 'expired']).update(status='expired')


class HostelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hostel.objects.annotate(
        score=Sum('missions__points', filter=Q(missions__status='cracked'))
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HostelDetailSerializer
        return HostelSerializer

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        hostels = self.get_queryset().order_by('-score')
        serializer = HostelSerializer(hostels, many=True)
        return Response(serializer.data)


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    permission_classes = [IsMissionOwnerOrReadOnly, IsStaffOrReadOnlyForCoreFields]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'difficulty', 'hostel']
    search_fields = ['codename', 'brief']
    throttle_scope = 'claim'

    def get_queryset(self):
        expire_overdue_missions()
        return Mission.objects.all()

    def get_throttles(self):
        if self.action == 'claim':
            return [ClaimMissionThrottle()]
        return super().get_throttles()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        locked_fields = {'codename', 'brief', 'points', 'difficulty', 'deadline', 'hostel'}
        if not request.user.is_staff:
            attempted = locked_fields & set(request.data.keys())
            if attempted:
                return Response(
                    {'detail': f"You cannot edit: {', '.join(attempted)}"},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], throttle_classes=[ClaimMissionThrottle])
    def claim(self, request, pk=None):
        expire_overdue_missions()
        mission = self.get_object()

        participant = getattr(request.user, 'participant', None)
        if participant is None:
            return Response({'detail': 'No participant profile linked to this user.'},
                             status=status.HTTP_400_BAD_REQUEST)

        if mission.status != 'unclaimed':
            return Response({'detail': f'Mission is already {mission.status}.'},
                             status=status.HTTP_400_BAD_REQUEST)

        if mission.deadline < timezone.now():
            mission.status = 'expired'
            mission.save()
            return Response({'detail': 'Mission deadline has passed.'},
                             status=status.HTTP_400_BAD_REQUEST)

        mission.claimed_by = participant
        mission.hostel = participant.hostel
        mission.status = 'in_progress'
        mission.save()
        return Response(MissionSerializer(mission).data)