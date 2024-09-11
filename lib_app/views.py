from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookForm, LentBookForm, ReturnBookForm, CustomUserCreationForm, CustomAuthenticationForm
from django.http import HttpResponse
from .models import Book, LentBook
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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



@login_required
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


@login_required
def singel(request, id): #show singel books
    book = Book.objects.get(pk=id)
    book_details = {
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
    }
    return render(request, 'singel.html', {'book_details': book_details})

@login_required
def update(request, id):  # Update book (title and optionally authors)
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()  # Save changes to title, other fields, and optionally authors
            return redirect('home')
        else:
            return HttpResponse('Invalid data!')
    else:  # If GET request   # Pre-populate authors with a comma-separated string of current authors
        authors = ', '.join([f"{author.first_name} {author.last_name}" for author in book.authors.all()])
        form = BookForm(instance=book, initial={'authors_input': authors})  # Pre-fill author field
    return render(request, 'update.html', {'form': form})

@login_required
def delete(request, id): #delete book
    book = get_object_or_404(Book, id=id)
    auhtor = list(book.authors.all())
    book.delete()
    
    for author in auhtor:
        if author.books.count() == 0:
            author.delete()
    return redirect('home')


@login_required
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


@login_required
def lent_book_list(request):
    # Get all lent books
    lent_books = LentBook.objects.all()

    return render(request, 'lent_book.html', {'lent_books': lent_books})



@login_required
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



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()

            # Auto login the user after registration
            login(request, user)

            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')  # Redirect to 'home' or another page
        else:
            messages.error(request, 'Invalid data! Please check the form.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Use Django's authenticate method
            user = authenticate(request, username=user_name, password=password)
            if user is not None:
                # Login the user
                login(request, user)
                return redirect('home')
            else:
                # Invalid credentials, show an error message
                messages.error(request, 'Invalid username or password')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')



def profile(request):
    return render(request, 'profile.html')
