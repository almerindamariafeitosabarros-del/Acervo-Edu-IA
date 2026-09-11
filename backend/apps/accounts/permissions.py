from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsManagerOrAdmin(BasePermission):
    """Gestor e Administrador."""

    message = 'Você não tem permissão para esta ação.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.can_manage_catalog)


class IsAdmin(BasePermission):
    """Apenas Administrador."""

    message = 'Apenas o Administrador pode executar esta ação.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.can_manage_users)


class ReadOnlyOrManager(BasePermission):
    """Leitura para qualquer usuário autenticado; escrita para Gestor/Admin."""

    message = 'Apenas Gestor ou Administrador pode alterar estes dados.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.can_manage_catalog


class ReadOnlyOrAdmin(BasePermission):
    """Leitura para qualquer usuário autenticado; escrita apenas para Admin."""

    message = 'Apenas o Administrador pode alterar estes dados.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.can_manage_users
