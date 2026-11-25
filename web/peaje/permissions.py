from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class EsAdministradorOLectura(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:

            return False

        if not request.user.activo:

            return False

        if request.method in SAFE_METHODS:

            return True

        return request.user.rol == "admin"