"""Decorators for role-based access control."""
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test


def role_required(*roles):
    """Decorator to check if user has required role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                return HttpResponseForbidden('Vous n\'avez pas accès à cette page.')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to require admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            return HttpResponseForbidden('Accès réservé aux administrateurs.')
        return view_func(request, *args, **kwargs)
    return wrapper


def representant_required(view_func):
    """Decorator to require representant role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'representant':
            return HttpResponseForbidden('Accès réservé aux représentants.')
        return view_func(request, *args, **kwargs)
    return wrapper


def encadrant_required(view_func):
    """Decorator to require encadrant role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'encadrant':
            return HttpResponseForbidden('Accès réservé aux encadrants.')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """Decorator to require student role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'etudiant':
            return HttpResponseForbidden('Accès réservé aux étudiants.')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_custom(view_func):
    """Simple login required decorator."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
