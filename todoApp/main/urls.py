from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name="home"),
    path('register/',views.register, name="register"),
    path('login/',views.signin, name="login"),
    path('logout/',views.signout, name="logout"),
    path('task/<int:id>', views.task, name="task"),
    path('create/',views.createTask, name="create"),
    path('update/<int:id>',views.editTask, name="update"),
    path('delete/<int:id>',views.removeTask, name="delete"),
    path('start/<int:id>',views.startTask, name="starttask"),
    path('end/<int:id>',views.endTask, name="endtask"),
]

