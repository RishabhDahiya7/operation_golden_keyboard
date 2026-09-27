from rest_framework.throttling import ScopedRateThrottle


class ClaimMissionThrottle(ScopedRateThrottle):
    scope = 'claim'