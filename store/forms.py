from django import forms
from . models import Product,Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
            'parent_cat',
            'description',
            'is_active',
            ]
        #excluded slug
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

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug']
