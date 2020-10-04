from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from accountancy.layouts import Div, LabelAndFieldAndErrors


class BaseContactForm(forms.ModelForm):
    class Meta:
        fields = ('code', 'name', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                LabelAndFieldAndErrors(
                    'code',
                    css_class="form-control form-control-sm w-100"
                ),
                css_class="form-group"
            ),
            Div(
                LabelAndFieldAndErrors(
                    'name',
                    css_class="form-control form-control-sm w-100"
                ),
                css_class="form-group"
            ),
            Div(
                LabelAndFieldAndErrors(
                    'email',
                    css_class="form-control form-control-sm w-100"
                ),
                css_class="form-group"
            ),
        )