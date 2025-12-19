import datetime
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.models import User
from .models import Book, BookCopy, Loan
from .serializers import RegisterSerializer, BookSerializer, LoanSerializer
from django.shortcuts import render
def is_librarian(user):
    return user.groups.filter(name__iexact='librarian').exists()
@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response({'data': serializer.data})
    elif request.method == 'POST':
        if not is_librarian(request.user):
            return Response({'message': 'You are not authorized to perform this action.'}, status = status.HTTP_403_FORBIDDEN)
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
        if not is_librarian(request.user):
            return Response({'message': 'You are not authorized to perform this action.'}, status = status.HTTP_403_FORBIDDEN)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_librarian(request.user):
            return Response({'message': 'You are not authorized to perform this action.'}, status = status.HTTP_403_FORBIDDEN)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def book_copies(request, book_id):
    copies = BookCopy.objects.filter(book_id=book_id)
    serializer = BookCopySerializer(copies, many=True)
    return Response(serializer.data)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book(request, loan_id):
    try:
        loan = Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if loan.user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    loan.status = 'returned'
    loan.return_date = datetime.date.today()
    loan.save()
    copy = loan.copy
    copy.status = 'available'
    copy.save()
    return Response({'detail': 'Book returned'}, status=status.HTTP_200_OK)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_fines(request):
    today = datetime.date.today()

    loans = Loan.objects.filter(
        user=request.user,
        fine_paid=False,
        due_date__lt=today,
        status__in=["borrowed", "overdue"],
    ).order_by("-due_date")

    serializer = LoanSerializer(loans, many=True)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_loans(request):
    """
    Returns all loans for the currently authenticated user.
    """
    loans = Loan.objects.filter(user=request.user).exclude(status='returned').order_by("-loan_date", "-due_date")
    serializer = LoanSerializer(loans, many=True)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_fine(request, loan_id):
    """
    Allows a user (or librarian) to pay the fine on their own loan.
    """
    try:
        loan = Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only the loan owner or a librarian can pay this fine
    is_librarian = request.user.groups.filter(name__iexact="librarian").exists()
    if loan.user != request.user and not is_librarian:
        return Response({"detail": "You cannot pay fines for other users."},
                        status=status.HTTP_403_FORBIDDEN)

    if loan.fine_paid:
        return Response({"detail": "Fine already paid."}, status=status.HTTP_400_BAD_REQUEST)

    fine_amount = loan.calculate_overdue_fine()
    if fine_amount <= 0:
        return Response({"detail": "No fine to pay."}, status=status.HTTP_400_BAD_REQUEST)

    # Mark paid
    loan.fine_paid = True
    loan.fine_paid_amount = fine_amount
    loan.save()

    serializer = LoanSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

