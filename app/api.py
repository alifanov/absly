from rest_framework import serializers, generics, permissions
from models import CanvasBlock, CanvasBlockItem

class CanvasBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = CanvasBlock
        fields = ('id', 'name')

class CanvasBlockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasBlockItem
        fields = ('id', 'name', 'level', 'block')

class CanvasBlockList(generics.ListCreateAPIView):
    model = CanvasBlock
    serializer_class = CanvasBlockSerializer
    permission_classes = [
        permissions.AllowAny
    ]

class CanvasBlockDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CanvasBlock
    serializer_class = CanvasBlockSerializer