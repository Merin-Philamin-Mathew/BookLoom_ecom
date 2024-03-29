from django import forms
from . models import Product,ProductVariant, AdditionalProductImages, Category, Author, Publication, Language

class CategoryForm(forms.ModelForm):
    cat_discount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage discount of max_price'}), required=False)
    class Meta:
        model = Category
        fields = [
            'category_name',
            'parent_cat',
            'cat_discount',
            'is_active',
            ]
        
        widgets = {
            #username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username"}))
            'category_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Category name'}),
            'parent_cat': forms.Select(attrs={'class': 'form-control','placeholder':'Parent'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

class ProductForm(forms.ModelForm):
    pro_discount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage discount of max_price'}), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'is_available':
                field.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug']

class ProductVariantForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = ProductVariant
        fields = '__all__'
        exclude = ['product_variant_slug','product']

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
            'author_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Author name'}),
            'about_author': forms.Textarea(attrs={'class': 'form-control','placeholder':'About Author'}),
            'author_image': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Author Image'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
    
class PublicationForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'name'}))
           
    class Meta:
        model = Publication
        fields = ['name','is_active',]   

class LanguageForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'name'}))
    
    class Meta:
        model = Language
        fields = ['name','is_active',]   
 