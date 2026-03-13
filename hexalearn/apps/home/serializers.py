from .models import Level
from rest_framework import serializers

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
