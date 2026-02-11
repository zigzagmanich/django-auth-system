from django.db import models
import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

class User(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Отчество')

    email = models.EmailField(unique=True, verbose_name='Email')
    password_hash = models.CharField(max_length=255, verbose_name='Хеш пароля')
    
    role = models.ForeignKey(
        'authorization.Role',  # Ссылка на модель Role
        on_delete=models.PROTECT,  # Нельзя удалить роль если есть пользователи
        verbose_name='Роль'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def set_password(self, password):
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            salt
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def generate_token(self):
        payload = {
            'user_id': self.id,
            'email': self.email,
            'role_id': self.role_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session_token = models.CharField(max_length=500, unique=True, verbose_name='Токен сессии')
    expires_at = models.DateTimeField(verbose_name='Истекает')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    user_agent = models.TextField(null=True, blank=True, verbose_name='User Agent')

    class Meta:
        db_table = 'sessions'
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"Session for {self.user.email}"

    def is_valid(self):
        return self.expires_at > timezone.now() and self.user.is_active
    
    @classmethod
    def create_session(cls, user, ip_address=None, user_agent=None):
        token = user.generate_token()
        expires_at = timezone.now() + timedelta(hours=24)
        
        session = cls.objects.create(
            user=user,
            session_token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return session