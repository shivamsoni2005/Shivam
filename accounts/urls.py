
from django.contrib import admin
from . import views


from django.urls import path
from .views import register_admin,register_student, signup, login_view
from django.http import JsonResponse, HttpResponse

def homePage(request):
    return HttpResponse('<h1>I am home page</h1>')



urlpatterns = [
   path('', homePage ),
   path('signup/',signup), #signup html page
#   path('login/',login), #login hmtl page
   path('login/',login_view), #login hmtl page
 #  path('dashboard/',dashboard),
   path('register_student/', register_student ),
   path('register_admin/', register_admin ),
   path("dashboard1/", views.dashboard1, name="dashboard1"),
   path("dashboard2/", views.dashboard2, name="dashboard2"),
   

]

# http://localhost:8000/accounts/dashboard