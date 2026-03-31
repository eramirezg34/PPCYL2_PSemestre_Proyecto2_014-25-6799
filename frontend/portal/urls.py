from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('ver-usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('tutor-panel/', views.tutor_panel, name='tutor_panel'),
    path('horarios/', views.horarios, name='horarios'),
    path('notas/', views.notas, name='notas'),
    path('reporte-notas/', views.reporte_notas, name='reporte_notas'),
    path('estudiante-panel/', views.estudiante_panel, name='estudiante_panel'),
]