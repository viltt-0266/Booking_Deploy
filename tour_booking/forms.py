from django import forms
from .models import Booking, Rating
from django.utils.translation import gettext_lazy as _

class TourSearchForm(forms.Form):
    query = forms.CharField(label=_('key search'), max_length=100, required=False)
    min_price = forms.DecimalField(label=_('Minimum Price'), min_value=0, required=False)
    max_price = forms.DecimalField(label=_('Maximum Price'), min_value=0, required=False)
    start_date = forms.DateField(label=_('Start day'), required=False)
    end_date = forms.DateField(label=_('End day'), required=False)
    location = forms.CharField(label=_('Address'), max_length=100, required=False)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_people', 'departure_date', 'end_date']  # Thêm trường 'end_date' vào form
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),  # Tùy chỉnh widget cho trường 'end_date'
        }
######################
from django import forms
from .models import Rating
from django.core.validators import MinValueValidator, MaxValueValidator

class RatingCommentForm(forms.ModelForm):
    rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        label='Rating',
        help_text='Choose a rating from 1 to 5.'
    )

    class Meta:
        model = Rating
        fields = ('rating', 'content')
