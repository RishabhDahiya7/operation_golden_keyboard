from rest_framework import permissions


class IsMissionOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the participant who claimed a mission can change its status.
    Anyone can read (GET) a mission. The 'claim' action is exempted here
    because eligibility for claiming is checked inside the view itself.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        if getattr(view, 'action', None) == 'claim':
            return True

        participant = getattr(request.user, 'participant', None)
        return participant is not None and obj.claimed_by_id == participant.id


class IsStaffOrReadOnlyForCoreFields(permissions.BasePermission):
    """
    Only staff can create/delete missions or edit core fields.
    Regular participants can still hit the endpoint for claim/status actions,
    but core-field edits are blocked at the serializer/view level too.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action in ['create', 'destroy']:
            return request.user and request.user.is_staff
        return request.user and request.user.is_authenticated