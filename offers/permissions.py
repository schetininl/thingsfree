from rest_framework import permissions


class IsOfferAuthorOrReadOnly(permissions.BasePermission): # не работает пока как надо - либо убрать либо откорректировать

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj.offer, 'author'):
            return obj.offer.author == request.user
        #elif hasattr(obj, 'user'): # пока непонятно зачем доп проверка, может убрать??
        #    return obj.user == request.user #  пока непонятно зачем доп проверка, может убрать??


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'): # пока непонятно зачем доп проверка, может убрать??
            return obj.user == request.user #  пока непонятно зачем доп проверка, может убрать??

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.is_admin

        return False
