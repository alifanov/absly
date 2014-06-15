from rest_framework import serializers, generics, permissions
from models import CanvasBlock

class CanvasBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = CanvasBlock
        fields = ('id', 'name')


class CanvasBlockList(generics.ListCreateAPIView, generics.DestroyAPIView):
    model = CanvasBlock
    serializer_class = CanvasBlockSerializer
    permission_classes = [
        permissions.AllowAny
    ]