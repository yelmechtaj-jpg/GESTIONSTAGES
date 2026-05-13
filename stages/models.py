from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    """Custom UserManager for email-based authentication."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Auto-generate username from email to satisfy AbstractUser constraint
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        REPRESENTANT = 'representant', 'Representant'
        ETUDIANT = 'etudiant', 'Etudiant'
        ENCADRANT = 'encadrant', 'Encadrant'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ETUDIANT)
    full_name = models.CharField(max_length=120)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = UserManager()

    def __str__(self) -> str:
        return self.full_name or self.email


class StageOffer(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PUBLISHED = 'published', 'Publiee'
        CLOSED = 'closed', 'Fermee'

    title = models.CharField(max_length=180)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        ACCEPTED = 'accepted', 'Acceptee'
        REJECTED = 'rejected', 'Rejetee'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    offer = models.ForeignKey(StageOffer, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.student} -> {self.offer}'


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Depose'
        APPROVED = 'approved', 'Approuve'
        REJECTED = 'rejected', 'Rejete'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    comment = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.original_name


class Defense(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planifiee'
        CONFIRMED = 'confirmed', 'Confirmee'
        DONE = 'done', 'Terminee'
        CANCELLED = 'cancelled', 'Annulee'

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='defenses')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='defenses_as_student')
    encadrant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='defenses_as_encadrant')
    scheduled_at = models.DateTimeField()
    room = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    notes = models.TextField(blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.student} - {self.scheduled_at:%d/%m/%Y %H:%M}'
