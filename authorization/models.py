from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name
    
class BusinessElement(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    endpoint = models.CharField(max_length=255, null=True, blank=True, verbose_name='API endpoint')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'business_elements'
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

    def __str__(self):
        return self.name
    

class AccessRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, verbose_name='Элемент')
    
    read_permission = models.BooleanField(default=False, verbose_name='Чтение своих')
    read_all_permission = models.BooleanField(default=False, verbose_name='Чтение всех')
    
    create_permission = models.BooleanField(default=False, verbose_name='Создание')
    
    update_permission = models.BooleanField(default=False, verbose_name='Изменение своих')
    update_all_permission = models.BooleanField(default=False, verbose_name='Изменение всех')
    
    delete_permission = models.BooleanField(default=False, verbose_name='Удаление своих')
    delete_all_permission = models.BooleanField(default=False, verbose_name='Удаление всех')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'access_rules'
        unique_together = [['role', 'element']]

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"