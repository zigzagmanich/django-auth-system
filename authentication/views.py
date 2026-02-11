from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from authentication.decorators import require_auth
from authentication.models import Session
from authentication.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer
)


@api_view(['POST'])
def register_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        session = Session.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        response_data = {
            'token': session.session_token,
            'user': UserSerializer(user).data,
            'expires_at': session.expires_at.isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@require_auth
def me_view(request):

    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@require_auth
def logout_view(request):
    
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    
    if token:
        Session.objects.filter(session_token=token).delete()
    
    return Response(
        {'message': 'Successfully logged out'},
        status=status.HTTP_200_OK
    )

@api_view(['PUT', 'PATCH'])
@require_auth
def update_profile_view(request):
    serializer = UserUpdateSerializer(
        request.user, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@require_auth
def delete_account_view(request):
    user = request.user
    
    user.is_active = False
    user.save()
    
    Session.objects.filter(user=user).delete()
    
    return Response(
        {'message': 'Account successfully deactivated'},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def test_auth_view(request):
    auth_user = getattr(request, '_authenticated_user', None)
    
    return Response({
        'has_authenticated_user_attr': auth_user is not None,
        'authenticated_user': str(auth_user) if auth_user else None,
        'authenticated_user_email': auth_user.email if auth_user else None,
        'request_user': str(request.user) if hasattr(request, 'user') and request.user else None,
    })