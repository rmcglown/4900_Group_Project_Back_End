from django.contrib import admin, messages
from .models import Author, Book, BookCopy, Loan
import datetime

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'publication_date')
    search_fields = ('title', 'isbn', 'author__first_name', 'author__last_name')
    list_filter =  ('genre', 'publication_date', 'author')

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
    search_fields = ('book__title',)

class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'copy', 'loan_date', 'due_date', 'return_date', 'status', 'fine_paid', 'fine_paid_amount', 'fine_paid_at', 'admin_current_fine')
    list_filter = ('status','loan_date', 'due_date', 'fine_paid', 'fine_paid_amount')
    search_fields = ('user__username', 'copy__book__title')
    readonly_fields = ('admin_current_fine',)
    actions = ['mark_fines_paid']

    def admin_current_fine(self, obj):
        try:
            val = obj.current_fine
        except Exception:
            return "-"
        return "-" if val is None else f"{val:.2f}"

    admin_current_fine.short_description = "Current fine (owed)"

    @admin.action(description="Mark selected loans' fines as paid (use current fine)")
    def mark_fines_paid(self, request, queryset):
        updated = 0
        for loan in queryset:
            fine = loan.calculate_overdue_fine()
            if fine > 0:
                loan.fine_paid_amount = fine
                loan.fine_paid = True
                if loan.status == 'overdue' and not loan.return_date:
                    loan.return_date = datetime.date.today()
                    loan.status = 'returned'
                loan.save()
                updated += 1
        self.message_user(request, f"Marked {updated} loan(s) as paid.", level=messages.SUCCESS)

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy, BookCopyAdmin)
admin.site.register(Loan, LoanAdmin)


