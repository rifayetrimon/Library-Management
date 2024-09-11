from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('singel/<int:id>/', views.singel, name='singel'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('lent/<int:book_id>/', views.lend_book, name='lent'),
    path('lent_book_list/', views.lent_book_list, name='lent_book_list'),
    path('return/', views.return_book, name='return'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]