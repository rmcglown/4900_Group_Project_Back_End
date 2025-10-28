from rest_framework import status, generics
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from django.shortcuts import render
@api_view(['GET'])
def book_list(request):
    if request.method == 'GET':
        movies = Book.objects.all()
        serializer = BookSerializer(movies, many=True)
        return Response({'data': serializer.data})


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

