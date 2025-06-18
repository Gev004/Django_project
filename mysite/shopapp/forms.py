from django import forms

from shopapp.models import Product,Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price','description']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'products','promocode','delivery_address']
        widgets = {
            'products': forms.CheckboxSelectMultiple,
        }


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(label="Choose a CSV File")