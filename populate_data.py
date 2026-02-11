import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User
from authorization.models import Role, BusinessElement, AccessRule


def create_users():
    print("Создание пользователей...")
    
    users_data = [
        {
            'email': 'admin@example.com',
            'first_name': 'Админ',
            'last_name': 'Администраторов',
            'password': 'admin123',
            'role_name': 'admin'
        },
        {
            'email': 'manager@example.com',
            'first_name': 'Менеджер',
            'last_name': 'Менеджеров',
            'password': 'manager123',
            'role_name': 'manager'
        },
        {
            'email': 'user@example.com',
            'first_name': 'Пользователь',
            'last_name': 'Пользователев',
            'password': 'user123',
            'role_name': 'user'
        },
        {
            'email': 'guest@example.com',
            'first_name': 'Гость',
            'last_name': 'Гостев',
            'password': 'guest123',
            'role_name': 'guest'
        },
    ]
    
    for user_data in users_data:
        role_name = user_data.pop('role_name')
        password = user_data.pop('password')
        
        role = Role.objects.get(name=role_name)
        
        if not User.objects.filter(email=user_data['email']).exists():
            user = User.objects.create(role=role, **user_data)
            user.set_password(password)
            user.save()
            print(f"Создан: {user.email} (пароль: {password})")
        else:
            print(f"Уже существует: {user_data['email']}")


def create_access_rules():
    print("\nСоздание правил доступа...")
    
    admin = Role.objects.get(name='admin')
    manager = Role.objects.get(name='manager')
    user = Role.objects.get(name='user')
    guest = Role.objects.get(name='guest')
    
    users_elem = BusinessElement.objects.get(name='users')
    products_elem = BusinessElement.objects.get(name='products')
    orders_elem = BusinessElement.objects.get(name='orders')
    stores_elem = BusinessElement.objects.get(name='stores')
    
    rules = [
        {
            'role': admin, 'element': users_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_all_permission': True, 'delete_all_permission': True
        },
        {
            'role': admin, 'element': products_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_all_permission': True, 'delete_all_permission': True
        },
        {
            'role': admin, 'element': orders_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_all_permission': True, 'delete_all_permission': True
        },
        {
            'role': admin, 'element': stores_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_all_permission': True, 'delete_all_permission': True
        },
        
        {
            'role': manager, 'element': users_elem,
            'read_all_permission': True
        },
        {
            'role': manager, 'element': products_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_all_permission': True, 'delete_all_permission': True
        },
        {
            'role': manager, 'element': orders_elem,
            'read_all_permission': True, 'create_permission': True,
            'update_permission': True
        },
        {
            'role': manager, 'element': stores_elem,
            'read_all_permission': True
        },
        
        {
            'role': user, 'element': users_elem,
            'read_permission': True, 'update_permission': True
        },
        {
            'role': user, 'element': products_elem,
            'read_all_permission': True
        },
        {
            'role': user, 'element': orders_elem,
            'read_permission': True, 'create_permission': True,
            'update_permission': True, 'delete_permission': True
        },
        
        {
            'role': guest, 'element': products_elem,
            'read_all_permission': True
        },
    ]
    
    for rule_data in rules:
        role = rule_data['role']
        element = rule_data['element']
        
        rule, created = AccessRule.objects.get_or_create(
            role=role,
            element=element,
            defaults={
                'read_permission': rule_data.get('read_permission', False),
                'read_all_permission': rule_data.get('read_all_permission', False),
                'create_permission': rule_data.get('create_permission', False),
                'update_permission': rule_data.get('update_permission', False),
                'update_all_permission': rule_data.get('update_all_permission', False),
                'delete_permission': rule_data.get('delete_permission', False),
                'delete_all_permission': rule_data.get('delete_all_permission', False),
            }
        )
        
        if created:
            print(f"Правило: {role.name} -> {element.name}")
        else:
            print(f"Уже есть: {role.name} -> {element.name}")


def main():
    create_users()
    create_access_rules()

if __name__ == '__main__':
    main()