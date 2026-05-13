"""Forms for stage management application."""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import StageOffer, Application, Document, Defense

User = get_user_model()


class StageOfferForm(forms.ModelForm):
    """Form for creating and editing stage offers."""
    
    class Meta:
        model = StageOffer
        fields = ['title', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'offre'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description détaillée'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class ApplicationForm(forms.ModelForm):
    """Form for student applications."""
    
    class Meta:
        model = Application
        fields = ['offer']
        widgets = {
            'offer': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        # Only show published offers
        self.fields['offer'].queryset = StageOffer.objects.filter(status='published')
    
    def clean(self):
        cleaned_data = super().clean()
        offer = cleaned_data.get('offer')
        
        if self.student and offer:
            # Check if student already applied
            if Application.objects.filter(student=self.student, offer=offer).exists():
                raise ValidationError('Vous avez déjà postulé à cette offre.')
        
        return cleaned_data


class ApplicationStatusForm(forms.Form):
    """Form for updating application status (representant only)."""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire (optionnel)'}),
    )


class DocumentForm(forms.ModelForm):
    """Form for document uploads."""
    
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (5MB max)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('Le fichier est trop volumineux (max 5MB).')
            
            # Validate file type
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'application/vnd.ms-excel',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
            if file.content_type not in allowed_types:
                raise ValidationError('Type de fichier non autorisé. Acceptés: PDF, Word, Excel.')
        
        return file


class DocumentReviewForm(forms.Form):
    """Form for encadrant to review documents."""
    STATUS_CHOICES = [
        ('uploaded', 'Téléchargé'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire pour l\'étudiant'}),
    )


class DefenseForm(forms.ModelForm):
    """Form for scheduling defenses."""
    
    class Meta:
        model = Defense
        fields = ['application', 'student', 'encadrant', 'scheduled_at', 'room', 'status']
        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'encadrant': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salle (ex: Amphi A, Bureau 201)'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show accepted applications
        self.fields['application'].queryset = Application.objects.filter(status='accepted')
        # Only show encadrants
        self.fields['encadrant'].queryset = User.objects.filter(role='encadrant')
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_at = cleaned_data.get('scheduled_at')
        room = cleaned_data.get('room')
        student = cleaned_data.get('student')
        encadrant = cleaned_data.get('encadrant')
        
        if scheduled_at and room:
            # Check for room conflicts (same room within 1 hour)
            time_range = [scheduled_at - timedelta(hours=1), scheduled_at + timedelta(hours=1)]
            conflicts = Defense.objects.filter(
                room=room,
                scheduled_at__range=time_range
            ).exclude(status='cancelled')
            
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            
            if conflicts.exists():
                raise ValidationError(f'Conflit horaire détecté dans la salle {room}.')
        
        if scheduled_at and student:
            # Check for student conflicts (same student within 1 hour)
            time_range = [scheduled_at - timedelta(hours=1), scheduled_at + timedelta(hours=1)]
            conflicts = Defense.objects.filter(
                student=student,
                scheduled_at__range=time_range
            ).exclude(status='cancelled')
            
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            
            if conflicts.exists():
                raise ValidationError(f'L\'étudiant a déjà une défense prévue à cette heure.')
        
        # Ensure scheduled_at is in the future
        if scheduled_at and scheduled_at < timezone.now():
            raise ValidationError('La date de défense doit être dans le futur.')
        
        return cleaned_data


class DefenseUpdateForm(forms.ModelForm):
    """Form for updating defense details (admin/encadrant only)."""
    
    class Meta:
        model = Defense
        fields = ['scheduled_at', 'room', 'status', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes internes'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_at = cleaned_data.get('scheduled_at')
        room = cleaned_data.get('room')
        
        if scheduled_at and scheduled_at < timezone.now():
            raise ValidationError('La date de défense doit être dans le futur.')
        
        if scheduled_at and room:
            # Check for conflicts
            time_range = [scheduled_at - timedelta(hours=1), scheduled_at + timedelta(hours=1)]
            conflicts = Defense.objects.filter(
                room=room,
                scheduled_at__range=time_range
            ).exclude(pk=self.instance.pk, status='cancelled')
            
            if conflicts.exists():
                raise ValidationError(f'Conflit horaire détecté dans la salle {room}.')
        
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """Form for password reset request."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'})
    )


class ResetPasswordForm(forms.Form):
    """Form for resetting password with token."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'}),
        min_length=8,
        help_text='Au moins 8 caractères'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}),
        label='Confirmer le mot de passe'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Les mots de passe ne correspondent pas.')
        
        return cleaned_data
