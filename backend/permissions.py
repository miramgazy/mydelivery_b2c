from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Доступ только для суперадминистратора"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superadmin
        )


class IsOrgAdmin(permissions.BasePermission):
    """Доступ только для администратора организации"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_org_admin
        )


class IsCustomer(permissions.BasePermission):
    """Доступ только для клиентов"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_customer
        )


class IsOwner(permissions.BasePermission):
    """Доступ только владельцу объекта"""
    
    def has_object_permission(self, request, view, obj):
        # Проверяем есть ли поле user у объекта
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsSameOrganization(permissions.BasePermission):
    """Доступ только для пользователей той же организации"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.organization:
            return False
        
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        
        return False


class ReadOnly(permissions.BasePermission):
    """Только чтение"""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS