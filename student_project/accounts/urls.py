from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('signup/', views.signup_view),
    path('activate/<int:uid>/', views.activate_account),
    path('logout/', views.logout_view),
    path('dashboard/', views.dashboard),
    path('add/', views.add_student),
    path('edit/<int:id>/', views.edit_student),
    path('delete/<int:id>/', views.delete_student),
]
