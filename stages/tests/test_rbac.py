from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from stages.models import Application, Defense, Document, StageOffer, User


class RBACViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com', password='pass12345', full_name='Admin', role=User.Role.ADMIN
        )
        self.representant = User.objects.create_user(
            email='rep@test.com', password='pass12345', full_name='Rep', role=User.Role.REPRESENTANT
        )
        self.etudiant = User.objects.create_user(
            email='etu@test.com', password='pass12345', full_name='Etu', role=User.Role.ETUDIANT
        )
        self.encadrant = User.objects.create_user(
            email='enc@test.com', password='pass12345', full_name='Enc', role=User.Role.ENCADRANT
        )

        self.offer = StageOffer.objects.create(
            title='Offer',
            description='Offer desc',
            status=StageOffer.Status.PUBLISHED,
        )
        self.application = Application.objects.create(
            student=self.etudiant,
            offer=self.offer,
            status=Application.Status.ACCEPTED,
        )
        self.document = Document.objects.create(
            student=self.etudiant,
            application=self.application,
            original_name='doc.pdf',
            file=SimpleUploadedFile('doc.pdf', b'pdfdata', content_type='application/pdf'),
        )
        self.defense = Defense.objects.create(
            application=self.application,
            student=self.etudiant,
            encadrant=self.encadrant,
            scheduled_at=timezone.now() + timedelta(days=1),
            room='R1',
            status=Defense.Status.PLANNED,
        )

    def test_offer_create_forbidden_for_student(self):
        self.client.force_login(self.etudiant)
        response = self.client.get(reverse('offer_create'))
        self.assertEqual(response.status_code, 403)

    def test_offer_create_allowed_for_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('offer_create'))
        self.assertEqual(response.status_code, 200)

    def test_application_list_forbidden_for_encadrant(self):
        self.client.force_login(self.encadrant)
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 403)

    def test_application_list_allowed_for_representant(self):
        self.client.force_login(self.representant)
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 200)

    def test_document_review_requires_encadrant(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('document_review', kwargs={'pk': self.document.pk}))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.encadrant)
        response = self.client.get(reverse('document_review', kwargs={'pk': self.document.pk}))
        self.assertEqual(response.status_code, 200)

    def test_defense_update_requires_admin(self):
        self.client.force_login(self.representant)
        response = self.client.get(reverse('defense_update', kwargs={'pk': self.defense.pk}))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.get(reverse('defense_update', kwargs={'pk': self.defense.pk}))
        self.assertEqual(response.status_code, 200)
