from django.contrib import admin, messages
from .models import Author, Book, BookCopy, Loan
from django.utils import timezone

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'publication_date')
    search_fields = ('title', 'isbn')
    list_filter =  ('genre',)

    actions = ["delete_all_books"]

    @admin.action(description="Delete ALL books")
    def delete_all_books(self, request, queryset):
        total = Book.objects.count()
        Book.objects.all().delete()
        self.message_user(
            request, f"Deleted {total} book(s).", level=messages.SUCCESS
        )

class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'added_date')
    list_filter = ('status', 'book')

class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'copy', 'loan_date', 'due_date', 'return_date', 'status')
    list_filter = ('status','loan_date', 'due_date')
    search_fields = ('user__username', 'copy__book__title')

    actions = ["mark_as_returned"]

    @admin.action(description="Return selected books")
    def mark_as_returned(self, request, queryset):
        count = 0
        for loan in queryset.filter(status="borrowed"):
            loan.copy.status = "available"
            loan.status = "returned"
            loan.return_date = timezone.now()
            loan.copy.save()
            loan.save()
            count += 1

        self.message_user(
            request,
            f"{count} book(s) successfully returned.",
            level=messages.SUCCESS
        )

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy, BookCopyAdmin)
admin.site.register(Loan, LoanAdmin)


