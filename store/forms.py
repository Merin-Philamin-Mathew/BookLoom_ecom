from django import forms
from . models import Product, Category, Author, Publication

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
            'parent_cat',
            'description',
            'is_active',
            ]
        
        widgets = {
            #username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username"}))
            'category_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Category name'}),
            'description': forms.TextInput(attrs={'class': 'form-control','placeholder':'Description'}),
            'parent_cat': forms.Select(attrs={'class': 'form-control','placeholder':'Parent'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

class ProductForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'is_available':
                field.widget.attrs['class'] = 'form-check-input'
            if field_name == 'image':
                field.widget.attrs['type'] = 'files'

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug']


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author

        fields = [
            'author_name',
            'about_author',
            'author_image',
            'is_active',
            ]
        widgets = {
            #username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username"}))
            'author_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Author name'}),
            'about_author': forms.TextInput(attrs={'class': 'form-control','placeholder':'About Author'}),
            'author_image': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Author Image'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
        labels = {
            'author_name': 'Name',
            'about_author': 'About Author',
            'author_image': 'Author Image',
            'is_active': 'Is Active',
        }

