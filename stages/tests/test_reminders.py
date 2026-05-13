from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail
from django.core.management import call_command
from datetime import timedelta

from stages.models import User, Application, StageOffer, Defense


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class DefenseReminderCommandTests(TestCase):
    def setUp(self):
        # create users
        self.student = User.objects.create_user(email='student@example.com', password='pass', full_name='Student')
        self.encadrant = User.objects.create_user(email='enc@example.com', password='pass', full_name='Encadrant')
        # create offer and application
        offer = StageOffer.objects.create(title='Test Offer', description='Desc', status='published')
        app = Application.objects.create(student=self.student, offer=offer)
        # schedule a defense within the reminder window
        self.defense = Defense.objects.create(
            application=app,
            student=self.student,
            encadrant=self.encadrant,
            scheduled_at=timezone.now() + timedelta(hours=6),
            room='Room 1',
            status=Defense.Status.PLANNED,
        )

    def test_send_defense_reminders_sends_emails_and_marks_sent(self):
        self.assertIsNone(self.defense.reminder_sent_at)
        # call command for next 24 hours
        call_command('send_defense_reminders', hours=24)
        # two emails should be in outbox (student + encadrant)
        self.assertEqual(len(mail.outbox), 2)
        # refresh from db and assert reminder_sent_at set
        self.defense.refresh_from_db()
        self.assertIsNotNone(self.defense.reminder_sent_at)
