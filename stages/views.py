import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, FileResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_http_methods
from datetime import timedelta

from .models import StageOffer, Application, Document, Defense, User
from .forms import (
    StageOfferForm, ApplicationForm, ApplicationStatusForm,
    DocumentForm, DocumentReviewForm, DefenseForm, DefenseUpdateForm,
    ForgotPasswordForm, ResetPasswordForm
)
from .decorators import (
    role_required, admin_required, representant_required,
    encadrant_required, student_required, login_required_custom
)

logger = logging.getLogger(__name__)


# ==================== Authentication ====================

def login_view(request: HttpRequest) -> HttpResponse:
    """User login view."""
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        logger.info(f"Login attempt: email={email}")
        user = authenticate(request, email=email, password=password)
        logger.info(f"Auth result: {user}")
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.full_name}!')
            return redirect('dashboard')
        error = 'Identifiants invalides.'
    return render(request, 'stages/login.html', {'error': error})


@login_required_custom
def logout_view(request: HttpRequest) -> HttpResponse:
    """User logout view."""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('login')


def forgot_password_view(request: HttpRequest) -> HttpResponse:
    """Forgot password request view."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse('reset_password', kwargs={'uidb64': uidb64, 'token': token})
                )
                subject = 'Réinitialisation de votre mot de passe'
                message = (
                    f'Bonjour {user.full_name or user.email},\n\n'
                    'Une demande de réinitialisation a été reçue pour votre compte.\n'
                    f'Cliquez sur ce lien pour définir un nouveau mot de passe : {reset_url}\n\n'
                    'Si vous n\'êtes pas à l\'origine de cette demande, vous pouvez ignorer cet email.'
                )
                send_mail(subject, message, None, [user.email])
                messages.success(request, 'Un lien de réinitialisation a été envoyé à votre email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.info(request, 'Si ce compte existe, vous recevrez un email.')
                return redirect('login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'stages/forgot_password.html', {'form': form})


def reset_password_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Reset password using a token sent by email."""
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_is_valid = user is not None and default_token_generator.check_token(user, token)
    if not token_is_valid:
        messages.error(request, 'Le lien de réinitialisation est invalide ou expiré.')
        return redirect('forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save(update_fields=['password'])
            messages.success(request, 'Votre mot de passe a été mis à jour. Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = ResetPasswordForm()

    return render(request, 'stages/reset_password.html', {'form': form, 'user_target': user})


# ==================== Dashboard ====================

def dashboard(request: HttpRequest) -> HttpResponse:
    """Role-based dashboard view."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'offers_count': StageOffer.objects.filter(status='published').count(),
    }
    
    if request.user.role == 'admin':
        context.update({
            'users_count': User.objects.count(),
            'applications_count': Application.objects.count(),
            'documents_count': Document.objects.count(),
            'defenses_count': Defense.objects.count(),
        })
    elif request.user.role == 'etudiant':
        context.update({
            'applications_count': request.user.applications.count(),
            'documents_count': request.user.documents.count(),
        })
    elif request.user.role == 'encadrant':
        context.update({
            'defenses_count': Defense.objects.filter(encadrant=request.user).count(),
            'documents_count': Document.objects.count(),
        })
    elif request.user.role == 'representant':
        context.update({
            'applications_count': Application.objects.count(),
            'pending_count': Application.objects.filter(status='pending').count(),
        })
    
    return render(request, 'stages/dashboard.html', context)


# ==================== Stage Offers CRUD ====================

def offer_list(request: HttpRequest) -> HttpResponse:
    """List all stage offers."""
    offers = StageOffer.objects.order_by('-created_at')
    return render(request, 'stages/offers_list.html', {'offers': offers})


def offer_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show offer details."""
    offer = get_object_or_404(StageOffer, pk=pk)
    applications_count = offer.applications.count()
    can_apply = False
    
    if request.user.is_authenticated and request.user.role == 'etudiant':
        can_apply = not Application.objects.filter(
            student=request.user, offer=offer
        ).exists() and offer.status == 'published'
    
    return render(request, 'stages/offer_detail.html', {
        'offer': offer,
        'applications_count': applications_count,
        'can_apply': can_apply,
    })


@admin_required
def offer_create(request: HttpRequest) -> HttpResponse:
    """Create new stage offer (admin only)."""
    if request.method == 'POST':
        form = StageOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre créée avec succès.')
            return redirect('offer_list')
    else:
        form = StageOfferForm()
    return render(request, 'stages/offer_form.html', {'form': form, 'title': 'Créer une offre'})


@admin_required
def offer_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update stage offer (admin only)."""
    offer = get_object_or_404(StageOffer, pk=pk)
    if request.method == 'POST':
        form = StageOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre mise à jour.')
            return redirect('offer_detail', pk=offer.pk)
    else:
        form = StageOfferForm(instance=offer)
    return render(request, 'stages/offer_form.html', {'form': form, 'title': 'Modifier une offre', 'offer': offer})


@admin_required
def offer_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete stage offer (admin only)."""
    offer = get_object_or_404(StageOffer, pk=pk)
    if request.method == 'POST':
        offer.delete()
        messages.success(request, 'Offre supprimée.')
        return redirect('offer_list')
    return render(request, 'stages/offer_confirm_delete.html', {'offer': offer})


# ==================== Applications ====================

@student_required
def application_create(request: HttpRequest, offer_id: int) -> HttpResponse:
    """Student applies for an offer."""
    offer = get_object_or_404(StageOffer, pk=offer_id, status='published')
    
    # Check if already applied
    if Application.objects.filter(student=request.user, offer=offer).exists():
        messages.warning(request, 'Vous avez déjà postulé à cette offre.')
        return redirect('offer_detail', pk=offer.pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, student=request.user)
        if form.is_valid():
            app = form.save(commit=False)
            app.student = request.user
            app.offer = offer
            app.save()
            messages.success(request, 'Candidature envoyée!')
            return redirect('application_detail', pk=app.pk)
    else:
        form = ApplicationForm(student=request.user, initial={'offer': offer})
    
    return render(request, 'stages/application_form.html', {'form': form, 'offer': offer})


@login_required_custom
def application_list(request: HttpRequest) -> HttpResponse:
    """List applications (filtered by role)."""
    if request.user.role == 'etudiant':
        applications = request.user.applications.select_related('offer')
    elif request.user.role == 'representant':
        applications = Application.objects.select_related('student', 'offer')
    else:
        return HttpResponseForbidden('Accès non autorisé.')
    
    return render(request, 'stages/application_list.html', {'applications': applications})


@login_required_custom
def application_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show application details."""
    application = get_object_or_404(Application, pk=pk)
    
    # Authorization check
    if (request.user != application.student and 
        request.user.role != 'representant' and 
        request.user.role != 'admin'):
        return HttpResponseForbidden('Accès non autorisé.')
    
    return render(request, 'stages/application_detail.html', {'application': application})


@representant_required
def application_update_status(request: HttpRequest, pk: int) -> HttpResponse:
    """Update application status (representant only)."""
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST)
        if form.is_valid():
            application.status = form.cleaned_data['status']
            application.save()
            messages.success(request, 'Statut mise à jour.')
            return redirect('application_detail', pk=application.pk)
    else:
        form = ApplicationStatusForm()
    
    return render(request, 'stages/application_status_form.html', {
        'form': form,
        'application': application,
    })


# ==================== Documents ====================

@student_required
def document_upload(request: HttpRequest, application_id: int = None) -> HttpResponse:
    """Upload a document (student only)."""
    application = None
    if application_id:
        application = get_object_or_404(Application, pk=application_id, student=request.user)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.student = request.user
            doc.application = application
            doc.original_name = form.cleaned_data['file'].name
            doc.save()
            messages.success(request, 'Document envoyé!')
            return redirect('document_list')
    else:
        form = DocumentForm()
    
    return render(request, 'stages/document_upload.html', {'form': form, 'application': application})


@login_required_custom
def document_list(request: HttpRequest) -> HttpResponse:
    """List documents (filtered by role)."""
    if request.user.role == 'etudiant':
        documents = request.user.documents.select_related('application')
    elif request.user.role == 'encadrant' or request.user.role == 'admin':
        documents = Document.objects.select_related('student', 'application')
    else:
        return HttpResponseForbidden('Accès non autorisé.')
    
    return render(request, 'stages/document_list.html', {'documents': documents})


@login_required_custom
def document_download(request: HttpRequest, pk: int) -> HttpResponse:
    """Download a document."""
    document = get_object_or_404(Document, pk=pk)
    
    # Authorization check
    if (request.user != document.student and 
        request.user.role not in ['encadrant', 'admin']):
        return HttpResponseForbidden('Accès non autorisé.')
    
    response = FileResponse(document.file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{document.original_name}"'
    return response


@encadrant_required
def document_review(request: HttpRequest, pk: int) -> HttpResponse:
    """Review a document (encadrant only)."""
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentReviewForm(request.POST)
        if form.is_valid():
            document.status = form.cleaned_data['status']
            document.comment = form.cleaned_data['comment']
            document.save()
            messages.success(request, 'Évaluation enregistrée.')
            return redirect('document_list')
    else:
        form = DocumentReviewForm()
    
    return render(request, 'stages/document_review.html', {
        'form': form,
        'document': document,
    })


# ==================== Defenses ====================

@admin_required
def defense_create(request: HttpRequest) -> HttpResponse:
    """Schedule a defense (admin only)."""
    if request.method == 'POST':
        form = DefenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Défense planifiée!')
            return redirect('defense_list')
    else:
        form = DefenseForm()
    
    return render(request, 'stages/defense_form.html', {'form': form, 'title': 'Planifier une défense'})


@login_required_custom
def defense_list(request: HttpRequest) -> HttpResponse:
    """List defenses (filtered by role)."""
    if request.user.role == 'etudiant':
        defenses = Defense.objects.filter(student=request.user).select_related('application', 'encadrant')
    elif request.user.role == 'encadrant':
        defenses = Defense.objects.filter(encadrant=request.user).select_related('student', 'application')
    elif request.user.role in ['admin', 'representant']:
        defenses = Defense.objects.select_related('student', 'encadrant', 'application')
    else:
        return HttpResponseForbidden('Accès non autorisé.')
    
    defenses = defenses.order_by('-scheduled_at')
    return render(request, 'stages/defense_list.html', {'defenses': defenses})


@login_required_custom
def defense_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show defense details."""
    defense = get_object_or_404(Defense, pk=pk)
    
    # Authorization check
    can_view = (request.user == defense.student or 
                request.user == defense.encadrant or
                request.user.role in ['admin', 'representant'])
    
    if not can_view:
        return HttpResponseForbidden('Accès non autorisé.')
    
    return render(request, 'stages/defense_detail.html', {'defense': defense})


@admin_required
def defense_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update defense (admin only)."""
    defense = get_object_or_404(Defense, pk=pk)
    
    if request.method == 'POST':
        form = DefenseUpdateForm(request.POST, instance=defense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Défense mise à jour.')
            return redirect('defense_detail', pk=defense.pk)
    else:
        form = DefenseUpdateForm(instance=defense)
    
    return render(request, 'stages/defense_form.html', {
        'form': form,
        'title': 'Modifier une défense',
        'defense': defense,
    })


@admin_required
def defense_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Cancel a defense (admin only)."""
    defense = get_object_or_404(Defense, pk=pk)
    if request.method == 'POST':
        defense.status = 'cancelled'
        defense.save()
        messages.success(request, 'Défense annulée.')
        return redirect('defense_list')
    return render(request, 'stages/defense_confirm_delete.html', {'defense': defense})
