from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Offer


class IsOfferAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        elif request.method == 'POST':
            return obj.author == request.user

        offer_obj = get_object_or_404(Offer, id=obj.offer.id)
        return offer_obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'author'):
            return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.is_admin

        return False
