from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import viewsets, permissions
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        participants = self.request.data.get('participants', [])
        if not participants:
            raise serializers.ValidationError('Participants are required')

        users = User.objects.filter(username__in=participants)
        if users.count() < 2:
            raise serializers.ValidationError('At least two participants are required')

        conversation = serializer.save()
        conversation.participants.set(users)
        conversation.save()

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if query:
            users = User.objects.filter(username__icontains=query)
            usernames = [user.username for user in users]
            return Response(usernames)
        return Response([])
