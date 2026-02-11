from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from authorization.models import Role, BusinessElement, AccessRule
from authorization.serializers import (
    RoleSerializer,
    BusinessElementSerializer,
    AccessRuleDetailSerializer,
    AccessRuleCreateUpdateSerializer
)


def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        user = getattr(request, '_authenticated_user', None)
        
        if not user:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not user.is_active:
            return JsonResponse({'error': 'Account is deactivated'}, status=401)
        
        request.user = user
        
        if user.role.name != 'admin':
            return JsonResponse(
                {'error': 'Forbidden', 'detail': 'Admin role required'},
                status=403
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

@api_view(['GET', 'POST'])
@require_admin
def roles_list_view(request):
    if request.method == 'GET':
        roles = Role.objects.all().order_by('id')
        serializer = RoleSerializer(roles, many=True)
        return Response({
            'count': roles.count(),
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@require_admin
def role_detail_view(request, pk):
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = RoleSerializer(role)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if role.user_set.exists():
            return Response(
                {'error': 'Cannot delete role with existing users'},
                status=status.HTTP_400_BAD_REQUEST
            )
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@require_admin
def role_access_rules_view(request, pk):
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    
    access_rules = AccessRule.objects.filter(role=role).select_related('element')
    serializer = AccessRuleDetailSerializer(access_rules, many=True)
    
    return Response({
        'role': RoleSerializer(role).data,
        'access_rules_count': access_rules.count(),
        'access_rules': serializer.data
    })


@api_view(['GET', 'POST'])
@require_admin
def business_elements_list_view(request):
    if request.method == 'GET':
        elements = BusinessElement.objects.all().order_by('id')
        serializer = BusinessElementSerializer(elements, many=True)
        return Response({
            'count': elements.count(),
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = BusinessElementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@require_admin
def business_element_detail_view(request, pk):
    try:
        element = BusinessElement.objects.get(pk=pk)
    except BusinessElement.DoesNotExist:
        return Response({'error': 'Business element not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BusinessElementSerializer(element)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BusinessElementSerializer(element, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@require_admin
def access_rules_list_view(request):

    if request.method == 'GET':
        access_rules = AccessRule.objects.all().select_related('role', 'element')
        
        role_id = request.query_params.get('role_id')
        element_id = request.query_params.get('element_id')
        
        if role_id:
            access_rules = access_rules.filter(role_id=role_id)
        if element_id:
            access_rules = access_rules.filter(element_id=element_id)
        
        access_rules = access_rules.order_by('role__name', 'element__name')
        serializer = AccessRuleDetailSerializer(access_rules, many=True)
        
        return Response({
            'count': access_rules.count(),
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = AccessRuleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            access_rule = serializer.save()
            return Response(
                AccessRuleDetailSerializer(access_rule).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@require_admin
def access_rule_detail_view(request, pk):
    try:
        access_rule = AccessRule.objects.select_related('role', 'element').get(pk=pk)
    except AccessRule.DoesNotExist:
        return Response({'error': 'Access rule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AccessRuleDetailSerializer(access_rule)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = AccessRuleCreateUpdateSerializer(
            access_rule,
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response(AccessRuleDetailSerializer(access_rule).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        access_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)