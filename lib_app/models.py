from django.db import models
from django.db import transaction
from django.utils import timezone

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=50)
    authors = models.ManyToManyField(Author, related_name='books')
    isbn = models.CharField(max_length=50)
    year = models.IntegerField()
    price = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.title



class LentBook(models.Model):
    borrower_name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    borrow_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.borrower_name} borrowed {self.quantity} of {self.book.title}"

    @transaction.atomic
    def lend_book(self):
        if self.book.quantity < self.quantity:
            raise ValueError("Not enough books in stock to lend.")
        
        # Subtract the lent quantity from the main book quantity
        self.book.quantity -= self.quantity
        self.book.save()
        
        # Save the LentBook record
        self.save()
