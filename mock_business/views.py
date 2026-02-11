from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from authorization.permissions import require_permission, PermissionChecker


# ============= Mock данные =============

MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук', 'price': 50000, 'owner_id': 2},
    {'id': 2, 'name': 'Телефон', 'price': 30000, 'owner_id': 2},
    {'id': 3, 'name': 'Планшет', 'price': 25000, 'owner_id': 3},
    {'id': 4, 'name': 'Наушники', 'price': 5000, 'owner_id': 3},
    {'id': 5, 'name': 'Клавиатура', 'price': 3000, 'owner_id': 1},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'quantity': 1, 'status': 'pending', 'owner_id': 3},
    {'id': 2, 'product_id': 2, 'quantity': 2, 'status': 'completed', 'owner_id': 3},
    {'id': 3, 'product_id': 3, 'quantity': 1, 'status': 'cancelled', 'owner_id': 4},
    {'id': 4, 'product_id': 4, 'quantity': 3, 'status': 'pending', 'owner_id': 4},
]


# ============= Утилиты =============

def filter_by_owner(items, user_id):
    """Фильтрация объектов по владельцу"""
    return [item for item in items if item.get('owner_id') == user_id]


def get_item_by_id(items, item_id):
    """Получение объекта по ID"""
    for item in items:
        if item['id'] == item_id:
            return item
    return None


# ============= Products API =============

@api_view(['GET', 'POST'])
@require_permission('products')
def products_list_view(request):
    """
    GET /api/products/ - список товаров
    POST /api/products/ - создание товара
    """
    if request.method == 'GET':
        products = MOCK_PRODUCTS.copy()
        
        # Если требуется фильтрация по owner (user видит только свои)
        if request.requires_owner_filter:
            products = filter_by_owner(products, request.user.id)
        
        return Response({
            'count': len(products),
            'results': products
        })
    
    elif request.method == 'POST':
        # Создание нового товара
        new_id = max([p['id'] for p in MOCK_PRODUCTS], default=0) + 1
        new_product = {
            'id': new_id,
            'name': request.data.get('name'),
            'price': request.data.get('price'),
            'owner_id': request.user.id
        }
        MOCK_PRODUCTS.append(new_product)
        
        return Response(new_product, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@require_permission('products')
def product_detail_view(request, pk):
    """
    GET /api/products/{id}/ - детали товара
    PUT /api/products/{id}/ - обновление товара
    DELETE /api/products/{id}/ - удаление товара
    """
    product = get_item_by_id(MOCK_PRODUCTS, pk)
    
    if not product:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверка прав для конкретного объекта
    action = PermissionChecker.get_action_from_method(request.method)
    permission = PermissionChecker.check_permission(
        request.user, 'products', action, product['owner_id']
    )
    
    if not permission['allowed']:
        return Response(
            {'error': 'Forbidden', 'detail': permission['message']},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        return Response(product)
    
    elif request.method == 'PUT':
        product['name'] = request.data.get('name', product['name'])
        product['price'] = request.data.get('price', product['price'])
        return Response(product)
    
    elif request.method == 'DELETE':
        MOCK_PRODUCTS.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============= Orders API =============

@api_view(['GET', 'POST'])
@require_permission('orders')
def orders_list_view(request):
    """
    GET /api/orders/ - список заказов
    POST /api/orders/ - создание заказа
    """
    if request.method == 'GET':
        orders = MOCK_ORDERS.copy()
        
        # Фильтрация по owner если требуется
        if request.requires_owner_filter:
            orders = filter_by_owner(orders, request.user.id)
        
        return Response({
            'count': len(orders),
            'results': orders
        })
    
    elif request.method == 'POST':
        new_id = max([o['id'] for o in MOCK_ORDERS], default=0) + 1
        new_order = {
            'id': new_id,
            'product_id': request.data.get('product_id'),
            'quantity': request.data.get('quantity', 1),
            'status': 'pending',
            'owner_id': request.user.id
        }
        MOCK_ORDERS.append(new_order)
        
        return Response(new_order, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@require_permission('orders')
def order_detail_view(request, pk):
    """
    GET /api/orders/{id}/ - детали заказа
    PUT /api/orders/{id}/ - обновление заказа
    DELETE /api/orders/{id}/ - удаление заказа
    """
    order = get_item_by_id(MOCK_ORDERS, pk)
    
    if not order:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверка прав для конкретного объекта
    action = PermissionChecker.get_action_from_method(request.method)
    permission = PermissionChecker.check_permission(
        request.user, 'orders', action, order['owner_id']
    )
    
    if not permission['allowed']:
        return Response(
            {'error': 'Forbidden', 'detail': permission['message']},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        return Response(order)
    
    elif request.method == 'PUT':
        order['status'] = request.data.get('status', order['status'])
        order['quantity'] = request.data.get('quantity', order['quantity'])
        return Response(order)
    
    elif request.method == 'DELETE':
        MOCK_ORDERS.remove(order)
        return Response(status=status.HTTP_204_NO_CONTENT)