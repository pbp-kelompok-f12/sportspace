from django import forms
from .models import Review, LapanganPadel

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['lapangan', 'comment', 'anonymous']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            reviewed_ids = Review.objects.filter(user=user).values_list("lapangan_id", flat=True)
            self.fields['lapangan'].queryset = LapanganPadel.objects.exclude(id__in=reviewed_ids)

        self.fields['lapangan'].widget.attrs.update({
            'class': 'w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-lime-500',
            'style': 'color: #1f2937;'  
        })
        self.fields['comment'].widget.attrs.update({
            'class': 'w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-lime-500',
            'style': 'color: #1f2937;',  
            'placeholder': 'Write your review here...'
        })
        self.fields['anonymous'].widget.attrs.update({
            'class': 'mr-2 rounded text-lime-600 focus:ring-lime-500',
        })

class EditReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'anonymous']  # ❌ tanpa lapangan

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['comment'].widget.attrs.update({
            'class': 'w-full border rounded-md px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-lime-500',
            'placeholder': 'Update your review...'
        })
