from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterUserSerializer
from .models import User
from .tasks import calculate_credit_score_task

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            calculate_credit_score_task.delay(str(user.id))
            return Response({
                'unique_user_id': user.id,
                'error': None
            }, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
