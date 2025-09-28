from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default serializer to add custom claims (data) to the token.
    """
    @classmethod
    def get_token(cls, user):
        # Call the base class method to get the token instance
        token = super().get_token(user)

        # Add custom claims here
        token['username'] = user.username
        # Assuming you have a 'role' field on your custom User model
        # token['role'] = user.role.name
        token['is_staff'] = user.is_staff

        return token