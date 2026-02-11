from rest_framework import serializers
from authorization.models import Role, BusinessElement, AccessRule


class RoleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class BusinessElementSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'description', 'endpoint', 'created_at']
        read_only_fields = ['id', 'created_at']


class AccessRuleDetailSerializer(serializers.ModelSerializer):
    
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)
    
    class Meta:
        model = AccessRule
        fields = [
            'id',
            'role', 'role_name',
            'element', 'element_name',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role_name', 'element_name', 'created_at', 'updated_at']


class AccessRuleCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccessRule
        fields = [
            'role', 'element',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission'
        ]
    
    def validate(self, data):
        role = data.get('role')
        element = data.get('element')
        
        if not self.instance:
            if AccessRule.objects.filter(role=role, element=element).exists():
                raise serializers.ValidationError(
                    f"Access rule for role '{role.name}' and element '{element.name}' already exists"
                )
        
        return data