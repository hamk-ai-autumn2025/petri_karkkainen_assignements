# mysite/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('home/', include('workout_program.urls')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),  # Redirect root to login
]
