from django.http import JsonResponse
from functools import wraps
from authorization.models import AccessRule, BusinessElement


class PermissionChecker:

    @staticmethod
    def get_action_from_method(method):
        method_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return method_map.get(method.upper())

    @staticmethod
    def check_permission(user, element_name, action, obj_owner_id=None):
        try:
            element = BusinessElement.objects.filter(name=element_name).first()
            if not element:
                return {
                    'allowed': False,
                    'requires_filter': False,
                    'message': f'Business element "{element_name}" not found'
                }

            access_rule = AccessRule.objects.filter(
                role=user.role,
                element=element
            ).first()

            if not access_rule:
                return {
                    'allowed': False,
                    'requires_filter': False,
                    'message': f'No access rule for role "{user.role.name}" and element "{element_name}"'
                }

            if action == 'create':
                allowed = access_rule.create_permission
                return {
                    'allowed': allowed,
                    'requires_filter': False,
                    'message': 'Access denied' if not allowed else 'Access granted'
                }

            if action == 'read':
                if access_rule.read_all_permission:
                    return {'allowed': True, 'requires_filter': False, 'message': 'Full read access'}
                elif access_rule.read_permission:
                    if obj_owner_id is None:
                        return {'allowed': True, 'requires_filter': True, 'message': 'Read own only'}
                    else:
                        is_owner = (obj_owner_id == user.id)
                        return {
                            'allowed': is_owner,
                            'requires_filter': False,
                            'message': 'Access denied - not owner' if not is_owner else 'Access granted'
                        }
                else:
                    return {'allowed': False, 'requires_filter': False, 'message': 'No read permission'}

            elif action == 'update':
                if access_rule.update_all_permission:
                    return {'allowed': True, 'requires_filter': False, 'message': 'Full update access'}
                elif access_rule.update_permission:
                    if obj_owner_id is None:
                        return {'allowed': True, 'requires_filter': True, 'message': 'Update own only'}
                    else:
                        is_owner = (obj_owner_id == user.id)
                        return {
                            'allowed': is_owner,
                            'requires_filter': False,
                            'message': 'Access denied - not owner' if not is_owner else 'Access granted'
                        }
                else:
                    return {'allowed': False, 'requires_filter': False, 'message': 'No update permission'}

            elif action == 'delete':
                if access_rule.delete_all_permission:
                    return {'allowed': True, 'requires_filter': False, 'message': 'Full delete access'}
                elif access_rule.delete_permission:
                    if obj_owner_id is None:
                        return {'allowed': True, 'requires_filter': True, 'message': 'Delete own only'}
                    else:
                        is_owner = (obj_owner_id == user.id)
                        return {
                            'allowed': is_owner,
                            'requires_filter': False,
                            'message': 'Access denied - not owner' if not is_owner else 'Access granted'
                        }
                else:
                    return {'allowed': False, 'requires_filter': False, 'message': 'No delete permission'}

        except Exception as e:
            return {
                'allowed': False,
                'requires_filter': False,
                'message': f'Permission check error: {str(e)}'
            }


def require_permission(element_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, '_authenticated_user', None)
            
            if not user:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            if not user.is_active:
                return JsonResponse(
                    {'error': 'Account is deactivated'},
                    status=401
                )

            request.user = user

            action = PermissionChecker.get_action_from_method(request.method)
            if not action:
                return JsonResponse(
                    {'error': 'Method not allowed'},
                    status=405
                )

            permission_result = PermissionChecker.check_permission(
                user=user,
                element_name=element_name,
                action=action
            )

            if not permission_result['allowed']:
                return JsonResponse(
                    {
                        'error': 'Forbidden',
                        'detail': permission_result['message']
                    },
                    status=403
                )
            
            request.requires_owner_filter = permission_result.get('requires_filter', False)

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator