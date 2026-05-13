from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import Application, Defense, Document, StageOffer, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'full_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(StageOffer)
class StageOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__email', 'student__full_name', 'offer__title')
    date_hierarchy = 'applied_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superusers see everything; staff are filtered by role where appropriate
        if request.user.is_superuser:
            return qs
        role = getattr(request.user, 'role', None)
        if role == User.Role.ETUDIANT:
            return qs.filter(student=request.user)
        if role == User.Role.REPRESENTANT:
            return qs
        if role == User.Role.ENCADRANT:
            return qs.filter(offer__applications__defenses__encadrant=request.user).distinct()
        return qs


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'student', 'status', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('original_name', 'student__email', 'student__full_name')
    date_hierarchy = 'uploaded_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        role = getattr(request.user, 'role', None)
        if role == User.Role.ETUDIANT:
            return qs.filter(student=request.user)
        if role == User.Role.ENCADRANT:
            return qs.filter(application__defenses__encadrant=request.user).distinct()
        return qs


@admin.register(Defense)
class DefenseAdmin(admin.ModelAdmin):
    list_display = ('student', 'encadrant', 'scheduled_at', 'room', 'status', 'reminder_sent_at')
    list_filter = ('status', 'scheduled_at')
    search_fields = ('student__full_name', 'encadrant__full_name', 'room')
    date_hierarchy = 'scheduled_at'
    readonly_fields = ('reminder_sent_at',)

    actions = ('mark_done', 'send_reminder')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        role = getattr(request.user, 'role', None)
        if role == User.Role.ENCADRANT:
            return qs.filter(encadrant=request.user)
        if role == User.Role.ETUDIANT:
            return qs.filter(student=request.user)
        return qs

    def mark_done(self, request, queryset):
        updated = queryset.update(status=Defense.Status.DONE)
        self.message_user(request, f"Marked {updated} defense(s) as done.")
    mark_done.short_description = 'Mark selected defenses as done'

    def send_reminder(self, request, queryset):
        from django.core.mail import send_mail
        from django.conf import settings
        sent = 0
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        for defense in queryset:
            if not defense.reminder_sent_at:
                subj = f"Rappel: soutenance prévue le {defense.scheduled_at.strftime('%d/%m/%Y %H:%M')}"
                body = (
                    f"Bonjour {defense.student.full_name},\n\n"
                    f"Rappel: votre soutenance est prévue le {defense.scheduled_at.strftime('%d/%m/%Y à %H:%M')} en salle {defense.room}.\n\n"
                )
                try:
                    send_mail(subj, body, from_email, [defense.student.email])
                    defense.reminder_sent_at = timezone.now()
                    defense.save(update_fields=['reminder_sent_at'])
                    sent += 1
                except Exception:
                    continue
        self.message_user(request, f"Sent {sent} reminder email(s).")
    send_reminder.short_description = 'Send reminder email for selected defenses'

