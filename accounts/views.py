from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

CustomUser = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(get_user_model(), username=username)

    if user.check_password(password):
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key, 'user': serializer.data})
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update the user profile information.

    This endpoint updates the profile information of the authenticated user
    based on the provided data.

    Parameters:
    - request (HttpRequest): The HTTP request object containing the user profile data in JSON format.

    Example:
    ```
    {
        "username": "new_username",
        "email": "new_email@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    ```

    Responses:
    - 200 OK: User profile updated successfully.
        {
            "id": 1,
            "username": "new_username",
            "email": "new_email@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    - 400 Bad Request: Invalid data provided.
        {
            "field_name": ["Error message 1", "Error message 2"]
        }

    Permissions:
    - The user must be authenticated.

    Returns:
    Response: A Response object containing the updated user profile data or validation errors.
    """
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_account(request):
    """
    Delete the user account associated with the current request.

    This endpoint deletes the user account of the authenticated user making the request.

    Example of usage:
    ```
    DELETE /api/delete_account/
    Headers:
        Authorization: Token <your_token_here>
    ```
    
    Parameters:
    - request (HttpRequest): The HTTP request object containing user authentication details.

    Returns:
    Response: A Response object with a JSON message indicating the success of the operation.
        Example:
        {
            "message": "Account deleted successfully"
        }
    """
    user = request.user
    user.delete()
    return Response({'message': 'Account deleted successfully'})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    Test endpoint to verify token-based authentication.

    This endpoint is used to verify that token-based authentication is working correctly.
    It requires authentication using either SessionAuthentication or TokenAuthentication,
    and the user must be authenticated (IsAuthenticated permission).

    Example of usage:
    ```
    GET /api/test_token/
    Headers:
        Authorization: Token <your_token_here>
    ```
    
    Parameters:
    - request (HttpRequest): The HTTP request object containing authentication details.

    Returns:
    Response: A Response object with a simple message indicating successful authentication.
        Example:
        HTTP 200 OK
        "passed!"
    """
    return Response("passed!")
