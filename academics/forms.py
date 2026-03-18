from django import forms
from .models import Semester, Course
from accounts.models import CustomUser


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['name', 'academic_year', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. S1-2025'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-2025'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ImportFileForm(forms.Form):
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all().order_by('-created_at'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the semester for this enrollment file"
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'}),
        help_text="Accepted formats: CSV, Excel (.xlsx, .xls)"
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        name = file.name.lower()
        if not (name.endswith('.csv') or name.endswith('.xlsx') or name.endswith('.xls')):
            raise forms.ValidationError("Only CSV and Excel files are accepted.")
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise forms.ValidationError("File size must be under 10MB.")
        return file

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['semester'].empty_label = "Select academic semester"
        self.fields['semester'].label_from_instance = (
            lambda s: f"{s.name} ({s.academic_year})"
        )


class AssignProfessorForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['professor']
        widgets = {
            'professor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professor'].queryset = CustomUser.objects.filter(role='professor', is_active=True)
        self.fields['professor'].empty_label = "--- Unassigned ---"


class WalkInStudentForm(forms.Form):
    matricule = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STU2024099'})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
