import datetime
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from django.shortcuts import render
@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response({'data': serializer.data})
    elif request.method == 'POST':
        if not request.user.groups.filter(name__iexact='librarian').exists():
            return Response({'message': 'You are not authorized to perform this action.'}, status = status.HTTP_401_UNAUTHORIZED)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def getBook(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_book(request, copy_id):

    try:
        copy = BookCopy.objects.get(id=copy_id)
    except BookCopy.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if copy.status != 'available':
        return Response(status=status.HTTP_403_FORBIDDEN)

    loan = Loan.objects.create(
        user=request.user,
        copy=copy,
        loan_date= datetime.date.today(),
        due_date= datetime.date.today() + datetime.timedelta(days=14),
        status='borrowed',
    )

    copy.status = 'on_loan'
    copy.save()

    serializer = LoanSerializer(loan)
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

