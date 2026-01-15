from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Разрешает доступ только суперадминистраторам
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or 
             (hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'superadmin'))
        )


class IsOrgAdmin(permissions.BasePermission):
    """
    Разрешает доступ администраторам организации
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role and 
            request.user.role.role_name == 'org_admin'
        )


class IsOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта
    """
    
    def has_object_permission(self, request, view, obj):
        # Если объект имеет атрибут user - проверяем его
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Если это сам User
        if isinstance(obj, type(request.user)):
            return obj == request.user
            
        return False
