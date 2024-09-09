from django import forms
from .models import Book, Author, LentBook

class BookForm(forms.ModelForm):
    # Custom author input field (comma-separated)
    authors_input = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
            'placeholder': 'Enter author names separated by commas',
        }), 
        label="Authors"
    )

    class Meta:
        model = Book
        fields = ['title', 'isbn', 'year', 'price', 'quantity', 'authors_input']

        # Customizing form widgets with padding-left for placeholders
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',  # Added pl-4 for padding-left
                'placeholder': 'Enter the book title',
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',  # Added pl-4 for padding-left
                'placeholder': 'Enter ISBN number',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',  # Added pl-4 for padding-left
                'placeholder': 'Enter the year of publication',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',  # Added pl-4 for padding-left
                'placeholder': 'Enter the price of the book',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',  # Added pl-4 for padding-left
                'placeholder': 'Enter quantity in stock',
            }),
        }
    

    def save(self, commit=True):
        book = super().save(commit=False)
        author_names = self.cleaned_data.get('authors_input', '').strip()

        if commit:
            book.save()

            if author_names:  # Only update authors if provided
                # Clear existing authors and add new ones
                book.authors.clear()
                author_list = [name.strip() for name in author_names.split(',') if name.strip()]

                for author_name in author_list:
                    name_parts = author_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    author, created = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
                    book.authors.add(author)

        return book
    

class LentBookForm(forms.ModelForm):
    class Meta:
        model = LentBook
        fields = ['borrower_name', 'book', 'quantity']
        
        widgets = {
            'borrower_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
                'placeholder': 'Enter borrower name',
            }),
            'book': forms.Select(attrs={
                'class': 'form-select mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg mb-4',
                'placeholder': 'Enter quantity to lend',
            }),
        }


class ReturnBookForm(forms.Form):
    borrower_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
            'placeholder': 'Borrower Name',
        }), 
        label="Borrower Name"
    )
    book_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
            'placeholder': 'Book Title',
        }), 
        label="Book Title"
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-input mt-1 block w-full h-12 pl-4 pr-4 rounded-lg',
            'placeholder': 'Quantity to Return',
        }), 
        label="Quantity"
    )