from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta

from stages.models import Defense


class Command(BaseCommand):
    help = 'Send email reminders for upcoming defenses and mark them as reminded.'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Send reminders for defenses within the next N hours (default: 24)')

    def handle(self, *args, **options):
        hours = options['hours']
        now = timezone.now()
        window_end = now + timedelta(hours=hours)

        qs = Defense.objects.filter(
            status__in=[Defense.Status.PLANNED, Defense.Status.CONFIRMED],
            scheduled_at__gte=now,
            scheduled_at__lte=window_end,
            reminder_sent_at__isnull=True,
        ).select_related('student', 'encadrant', 'application')

        total = qs.count()
        if total == 0:
            self.stdout.write('No upcoming defenses to remind.')
            return

        self.stdout.write(f'Found {total} defense(s) to notify (within next {hours} hours).')

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        for defense in qs:
            subject = f"Rappel: soutenance prévue le {defense.scheduled_at.strftime('%d/%m/%Y %H:%M')}"
            body = (
                f"Bonjour {defense.student.full_name},\n\n"
                f"Ceci est un rappel pour votre soutenance de stage prévue le {defense.scheduled_at.strftime('%d/%m/%Y à %H:%M')} dans la salle {defense.room}.\n\n"
                "Merci de vous présenter 10 minutes avant l\'heure prévue.\n\n"
                "Cordialement,\nL'équipe de gestion des stages"
            )

            try:
                send_mail(subject, body, from_email, [defense.student.email])
                self.stdout.write(f'Notified student: {defense.student.email}')
            except Exception as e:
                self.stderr.write(f'Failed to send student email for defense {defense.pk}: {e}')

            # Notify encadrant
            enc_subject = f"Rappel: soutenance de {defense.student.full_name} le {defense.scheduled_at.strftime('%d/%m/%Y %H:%M')}"
            enc_body = (
                f"Bonjour {defense.encadrant.full_name},\n\n"
                f"La soutenance de {defense.student.full_name} est prévue le {defense.scheduled_at.strftime('%d/%m/%Y à %H:%M')} en salle {defense.room}.\n\n"
                "Merci de vérifier que tout est prêt et d'assister à la soutenance.\n\n"
                "Cordialement,\nL'équipe de gestion des stages"
            )

            try:
                send_mail(enc_subject, enc_body, from_email, [defense.encadrant.email])
                self.stdout.write(f'Notified encadrant: {defense.encadrant.email}')
            except Exception as e:
                self.stderr.write(f'Failed to send encadrant email for defense {defense.pk}: {e}')

            defense.reminder_sent_at = timezone.now()
            defense.save(update_fields=['reminder_sent_at'])

        self.stdout.write('Reminders processed.')
