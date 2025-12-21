from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import Client
from .serializers import ClientSerializer, ClientBalanceSerializer


# Authentication views
def login_view(request):
    """Display login page"""
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')


def register_view(request):
    """Display registration page"""
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'register.html')


# Template views
@login_required
def client_list_view(request):
    """Display list of all clients"""
    return render(request, 'clients_list.html')


@login_required
def client_detail_view(request, pk):
    """Display client detail page"""
    return render(request, 'client_detail.html', {'client_id': pk})


# API ViewSet
class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client model.
    Provides CRUD operations and custom actions.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Allow registration and login without authentication."""
        if self.action in ['create', 'register', 'login']:
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get detailed balance information for a client."""
        client = self.get_object()
        serializer = ClientBalanceSerializer(client)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new client."""
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login a client."""
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            serializer = ClientSerializer(user)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout the current client."""
        logout(request)
        return Response({'message': 'Successfully logged out'})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = ClientSerializer(request.user)
        return Response(serializer.data)
