from rest_framework import serializers
from authentication.models import User
from authorization.models import Role


class UserRegistrationSerializer(serializers.Serializer):
    
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True, required=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value.lower()
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        default_role = Role.objects.get(name='user')
        
        user = User.objects.create(role=default_role, **validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        try:
            user = User.objects.select_related('role').get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    
    role = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'middle_name', 
                  'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.save()
        return instance