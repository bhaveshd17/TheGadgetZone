from django.forms import ModelForm
from .models import Product

class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
