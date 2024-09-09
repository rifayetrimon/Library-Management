from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookForm, LentBookForm, ReturnBookForm
from django.http import HttpResponse
from .models import Book, LentBook

# Create your views here.



def create(request): #add new book
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            return HttpResponse('Invalid data!')

    return render(request, 'create.html', {'form': BookForm()})




def home(request): #show all books
    books = Book.objects.all()
    result = []
    for book in books:
        result.append({
            'id': book.pk,
            'title': book.title,
            'author': {
                f'{author.first_name} {author.last_name}'
                for author in book.authors.all()
            },
            'isbn': book.isbn,
            'year': book.year,
            'price': book.price,
            'quantity': book.quantity
        })

    return render(request, 'home.html', {'books': result })



def singel(request, id): #show singel books
    book = Book.objects.get(pk=id)
    book_details = {
        'id': book.pk,
        'title': book.title,
        'author': [
            f'{author.first_name} {author.last_name}'
            for author in book.authors.all()
            ],
        'isbn': book.isbn,
        'year': book.year,
        'price': book.price,
        'quantity': book.quantity   
    }
    return render(request, 'singel.html', {'book_details': book_details})


def update(request, id):  # Update book (title and optionally authors)
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()  # Save changes to title, other fields, and optionally authors
            return redirect('home')
        else:
            return HttpResponse('Invalid data!')

    else:  # If GET request
        # Pre-populate authors with a comma-separated string of current authors
        authors = ', '.join([f"{author.first_name} {author.last_name}" for author in book.authors.all()])
        form = BookForm(instance=book, initial={'authors_input': authors})  # Pre-fill author field
    
    return render(request, 'update.html', {'form': form})


# def update(request, id):  # Update book
#     book = Book.objects.get(id=id)

#     if request.method == 'POST':
#         form = BookForm(request.POST, instance=book)
#         if form.is_valid():
#             book = form.save(commit=False)
            
#             # Get the author input from the form
#             author_names = form.cleaned_data['authors_input'].split(',')
#             book.authors.clear()  # Clear existing authors
            
#             for name in author_names:
#                 name = name.strip()
#                 if name:  # Only if name is not empty
#                     # Assuming authors' names are provided in "First Last" format
#                     first_name, last_name = name.split(' ', 1)
#                     author, created = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
#                     book.authors.add(author)
                    
#             book.save()
#             return redirect('home')
#         else:
#             return HttpResponse('Invalid data!')

#     else:  # If GET request
#         # Pre-populate the author field with a comma-separated string of authors
#         authors = ', '.join([f"{author.first_name} {author.last_name}" for author in book.authors.all()])
#         form = BookForm(instance=book, initial={'authors_input': authors})  # Set initial value for authors
    
#     return render(request, 'update.html', {'form': form})


def delete(request, id): #delete book
    book = Book.objects.get(id=id)
    book.delete()
    return redirect('home')



def lend_book(request, book_id=None):
    # Pre-populate the form with the selected book
    book = get_object_or_404(Book, id=book_id) if book_id else None
    
    if request.method == 'POST':
        form = LentBookForm(request.POST)
        if form.is_valid():
            lent_book = form.save(commit=False)
            
            # Use the lend_book method to handle book quantity update and saving
            try:
                lent_book.book = book  # Set the pre-selected book
                lent_book.lend_book()  # Reduce the book quantity and save the lending record
                return redirect('lent_book_list')  # Redirect to lent book list
            except ValueError as e:
                # Handle insufficient stock error
                return render(request, 'lent.html', {'form': form, 'error': str(e)})
    else:
        form = LentBookForm(initial={'book': book})  # Pre-populate the book

    return render(request, 'lent.html', {'form': form})



def lent_book_list(request):
    # Get all lent books
    lent_books = LentBook.objects.all()

    return render(request, 'lent_book.html', {'lent_books': lent_books})




def return_book(request):
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            borrower_name = form.cleaned_data['borrower_name']  # Correct way to get POST data via the form
            book_title = form.cleaned_data['book_title']
            quantity = form.cleaned_data['quantity']

            # Fetch LentBook entry
            lent_book = get_object_or_404(LentBook, borrower_name=borrower_name, book__title=book_title)

            if lent_book.quantity < quantity:
                return HttpResponse("You cannot return more books than borrowed!")

            lent_book.quantity -= quantity
            if lent_book.quantity == 0:
                lent_book.delete()
            else:
                lent_book.save()

            book = lent_book.book
            book.quantity += quantity  # Increase book quantity back
            book.save()

            return redirect('lent_book_list')  # Redirect to lent book list

        else:
            return HttpResponse("Invalid form data")

    else:
        form = ReturnBookForm()  # Render empty form on GET request
        return render(request, 'return_book.html', {'form': form})

