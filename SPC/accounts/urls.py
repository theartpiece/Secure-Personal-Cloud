from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    # path('login/', views.SignUp.as_view(), name='signup'),
    # path('logout/', views.SignUp.as_view(), name='signup'),

]

