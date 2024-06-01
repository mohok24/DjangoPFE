"""
Definition of forms.
"""

from django import forms

class ReportSearchForm(forms.Form):
    patient_id = forms.IntegerField(required=False)  
    patient_name = forms.CharField(max_length=100, required=False)
    dates = forms.ChoiceField(choices=[('exact', 'Exact date'), ('range', 'Range')], widget=forms.RadioSelect)
    date = forms.DateField(label='Date', required=False)
    type = forms.CharField(label='Type', required=False)
    indication = forms.CharField(label='Indication', required=False)
    leftM = forms.CharField(label='Left M', required=False)
    rightM = forms.CharField(label='Right M', required=False)
    bothM = forms.CharField(label='Both M', required=False)
    leftE = forms.CharField(label='Left E', required=False)
    rightE = forms.CharField(label='Right E', required=False)
    bothE = forms.CharField(label='Both E', required=False)
    classification = forms.CharField(label='Classification', required=False)
    conclusion = forms.CharField(label='Conclusion', required=False)
    recommendations = forms.CharField(label='Recommendations', required=False)
    from_date = forms.DateField(required=False) 
    to_date = forms.DateField(required=False)
    
class PatientSearchForm(forms.Form):
    id = forms.IntegerField(required=False)
    firstname = forms.CharField(label='firstname',required=False)
    lastname = forms.CharField(label='lastname',required=False)
    age = forms.IntegerField(label='age',required=False)
    
from app.models import Message

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    receiver = forms.CharField(max_length=100)  

    class Meta:
        model = Message
        fields = ['subject','content', 'image']  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False 

from django import forms
from .models import Report

class EditableDivWidget(forms.Widget):
    template_name = 'editable_div.html'

    def __init__(self, attrs=None):
        default_attrs = {'contenteditable': 'true'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context

from django import forms
from .models import Report

class EditableDivWidget(forms.Widget):
    template_name = 'editable_div.html'

    def __init__(self, attrs=None):
        default_attrs = {'contenteditable': 'true'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context

class ReportForm(forms.ModelForm):
   

    class Meta:
        model = Report
        fields = ['user', 'date', 'type', 'indication', 'leftM', 'rightM', 'bothM', 'leftE', 'rightE', 'bothE', 'leftclassification', 'rightclassification', 'bothclassification', 'conclusion', 'recommendations']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'indication': EditableDivWidget(attrs={'rows': 3}),
            'leftM': EditableDivWidget(attrs={'rows': 3}),
            'rightM': EditableDivWidget(attrs={'rows': 3}),
            'bothM': EditableDivWidget(attrs={'rows': 3}),
            'leftE': EditableDivWidget(attrs={'rows': 3}),
            'rightE': EditableDivWidget(attrs={'rows': 3}),
            'bothE': EditableDivWidget(attrs={'rows': 3}),
            'leftclassification': EditableDivWidget(attrs={'rows': 3}),
            'rightclassification': EditableDivWidget(attrs={'rows': 3}),
            'bothclassification': EditableDivWidget(attrs={'rows': 3}),
            'conclusion': EditableDivWidget(attrs={'rows': 3}),
            'recommendations': EditableDivWidget(attrs={'rows': 3}),
            'type': EditableDivWidget(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        if self.request and self.request.user:
            self.fields['user'].initial = self.request.user
            self.fields['user'].widget = forms.HiddenInput()

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Upload DOCX File')