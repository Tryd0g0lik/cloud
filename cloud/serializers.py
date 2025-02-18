from rest_framework import serializers

from cloud_user.models import UserRegister


class AdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserRegister
        fields = "__all__"
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
        # extra_kwargs = {'password': {'write_only': True}}
        
    