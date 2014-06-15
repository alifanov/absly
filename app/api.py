from rest_framework import serializers
from models import CanvasBlock

class CanvasBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = CanvasBlock
        fields = ('id', 'name')
