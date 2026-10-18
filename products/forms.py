from django import forms


class ReviewForm(forms.Form):
    text = forms.CharField(
        label="نظر شما",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "نظر خود را بنویسید..."}),
    )
    rating = forms.ChoiceField(
        label="نمره از ۵",
        required=False,
        choices=[("", "انتخاب نمره")] + [(str(i), str(i)) for i in range(1, 6)],
    )
