from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Subscription
from .serializers.serializers import SubscriptionSerializer
from .models import User
from .serializers.serializers import UserSerializer
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: 'User created successfully'},
        operation_summary="Register a new user",
        operation_description="Endpoint for user registration. Returns a JWT token after successful registration.",
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        """
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user.jwt_token = str(refresh.access_token)
        user.save()
