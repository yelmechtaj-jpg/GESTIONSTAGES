"""URL routing for stages app."""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_view, name='reset_password'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Stage Offers
    path('offers/', views.offer_list, name='offer_list'),
    path('offers/<int:pk>/', views.offer_detail, name='offer_detail'),
    path('offers/create/', views.offer_create, name='offer_create'),
    path('offers/<int:pk>/edit/', views.offer_update, name='offer_update'),
    path('offers/<int:pk>/delete/', views.offer_delete, name='offer_delete'),
    
    # Applications
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('offers/<int:offer_id>/apply/', views.application_create, name='application_create'),
    path('applications/<int:pk>/status/', views.application_update_status, name='application_update_status'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
    path('documents/<int:pk>/review/', views.document_review, name='document_review'),
    
    # Defenses
    path('defenses/', views.defense_list, name='defense_list'),
    path('defenses/create/', views.defense_create, name='defense_create'),
    path('defenses/<int:pk>/', views.defense_detail, name='defense_detail'),
    path('defenses/<int:pk>/edit/', views.defense_update, name='defense_update'),
    path('defenses/<int:pk>/delete/', views.defense_delete, name='defense_delete'),
]
