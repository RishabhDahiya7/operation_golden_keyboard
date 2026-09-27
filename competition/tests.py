from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Hostel, Participant, Mission


class MissionAPITests(APITestCase):
    def setUp(self):
        self.hostel1, _ = Hostel.objects.get_or_create(name="Gandhi Bhawan")
        self.hostel2, _ = Hostel.objects.get_or_create(name="Krishna Bhawan")

        self.user1 = User.objects.create_user(username="alice", password="pass1234")
        self.participant1 = Participant.objects.create(
            user=self.user1, handle="alice_h", hostel=self.hostel1
        )

        self.user2 = User.objects.create_user(username="bob", password="pass1234")
        self.participant2 = Participant.objects.create(
            user=self.user2, handle="bob_h", hostel=self.hostel2
        )

        self.staff_user = User.objects.create_user(
            username="staff", password="pass1234", is_staff=True
        )

        self.future_mission = Mission.objects.create(
            codename="FutureMission",
            brief="test",
            points=100,
            difficulty="easy",
            status="unclaimed",
            deadline=timezone.now() + timedelta(days=1),
        )

        self.expired_mission = Mission.objects.create(
            codename="ExpiredMission",
            brief="test",
            points=50,
            difficulty="easy",
            status="unclaimed",
            deadline=timezone.now() - timedelta(days=1),
        )

    def test_claim_available_mission_success(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.post(f"/api/missions/{self.future_mission.id}/claim/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(response.data["hostel"], self.hostel1.id)

    def test_double_claim_fails(self):
        self.client.login(username="alice", password="pass1234")
        self.client.post(f"/api/missions/{self.future_mission.id}/claim/")
        self.client.logout()

        self.client.login(username="bob", password="pass1234")
        response = self.client.post(f"/api/missions/{self.future_mission.id}/claim/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_claim_expired_mission_fails(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.post(f"/api/missions/{self.expired_mission.id}/claim/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_participant_cannot_edit_another_mission(self):
        self.client.login(username="alice", password="pass1234")
        self.client.post(f"/api/missions/{self.future_mission.id}/claim/")
        self.client.logout()

        self.client.login(username="bob", password="pass1234")
        response = self.client.patch(
            f"/api/missions/{self.future_mission.id}/",
            {"status": "cracked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_cannot_edit_core_fields(self):
        self.client.login(username="alice", password="pass1234")
        self.client.post(f"/api/missions/{self.future_mission.id}/claim/")
        response = self.client.patch(
            f"/api/missions/{self.future_mission.id}/",
            {"points": 999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_edit_core_fields(self):
        self.client.login(username="staff", password="pass1234")
        response = self.client.patch(
            f"/api/missions/{self.future_mission.id}/",
            {"points": 999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["points"], 999)

    def test_leaderboard_reflects_cracked_missions_only(self):
        self.future_mission.claimed_by = self.participant1
        self.future_mission.hostel = self.hostel1
        self.future_mission.status = "cracked"
        self.future_mission.save()

        response = self.client.get("/api/leaderboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        gandhi = next(h for h in response.data if h["name"] == "Gandhi Bhawan")
        self.assertEqual(gandhi["score"], 100)