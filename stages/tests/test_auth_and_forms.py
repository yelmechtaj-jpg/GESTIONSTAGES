import re
from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from stages.forms import DefenseForm
from stages.models import Application, Defense, StageOffer, User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthAndFormTests(TestCase):
    def setUp(self):
        self.password = 'Testpass123'
        self.user = User.objects.create_user(
            email='student@example.com',
            password=self.password,
            full_name='Student One',
            role=User.Role.ETUDIANT,
        )

    def test_login_view_authenticates_with_email(self):
        response = self.client.post(reverse('login'), {
            'email': self.user.email,
            'password': self.password,
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_forgot_password_sends_reset_email_and_reset_view_updates_password(self):
        response = self.client.post(reverse('forgot_password'), {'email': self.user.email})

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(len(mail.outbox), 1)

        body = mail.outbox[0].body
        match = re.search(r'/reset-password/([^/]+)/([^/]+)/', body)
        self.assertIsNotNone(match)

        uidb64, token = match.groups()
        reset_url = reverse('reset_password', kwargs={'uidb64': uidb64, 'token': token})

        get_response = self.client.get(reset_url)
        self.assertEqual(get_response.status_code, 200)

        new_password = 'Newpass123'
        post_response = self.client.post(reset_url, {
            'password': new_password,
            'password_confirm': new_password,
        })

        self.assertRedirects(post_response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_defense_form_rejects_room_conflict(self):
        offer = StageOffer.objects.create(title='Offer 1', description='Desc', status='published')
        application = Application.objects.create(student=self.user, offer=offer, status=Application.Status.ACCEPTED)
        encadrant = User.objects.create_user(
            email='encadrant@example.com',
            password='Encpass123',
            full_name='Encadrant User',
            role=User.Role.ENCADRANT,
        )
        scheduled_at = timezone.now() + timedelta(days=1)

        Defense.objects.create(
            application=application,
            student=self.user,
            encadrant=encadrant,
            scheduled_at=scheduled_at,
            room='Room A',
            status=Defense.Status.PLANNED,
        )

        form = DefenseForm(data={
            'application': application.pk,
            'student': self.user.pk,
            'encadrant': encadrant.pk,
            'scheduled_at': (scheduled_at + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M'),
            'room': 'Room A',
            'status': Defense.Status.PLANNED,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('Conflit horaire détecté dans la salle Room A.', str(form.errors))
