from rest_framework import serializers, generics, permissions
from models import CanvasBlock, CanvasBlockItem

class CanvasBlockSerializer(serializers.ModelSerializer):
    elements = serializers.RelatedField(many=True)

    class Meta:
        model = CanvasBlock
        fields = ('id', 'name', 'elements')

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

class CanvasBlockItemList(generics.ListCreateAPIView):
    model = CanvasBlockItem
    serializer_class = CanvasBlockItemSerializer
    permission_classes = [
        permissions.AllowAny
    ]

class CanvasBlockItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CanvasBlockItem
    serializer_class = CanvasBlockItemSerializer