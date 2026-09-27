from rest_framework import serializers
from .models import Hostel, Participant, Mission


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'handle', 'hostel', 'user']


class MissionSerializer(serializers.ModelSerializer):
    claimed_by_handle = serializers.CharField(source='claimed_by.handle', read_only=True)
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)

    class Meta:
        model = Mission
        fields = [
            'id', 'codename', 'brief', 'points', 'difficulty', 'status', 'deadline',
            'claimed_by', 'claimed_by_handle', 'hostel', 'hostel_name',
        ]
        read_only_fields = ['claimed_by', 'hostel']


class HostelSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hostel
        fields = ['id', 'name', 'score']


class HostelDetailSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only=True)
    cracked_missions = serializers.SerializerMethodField()

    class Meta:
        model = Hostel
        fields = ['id', 'name', 'score', 'cracked_missions']

    def get_cracked_missions(self, obj):
        cracked = obj.missions.filter(status='cracked')
        return MissionSerializer(cracked, many=True).data