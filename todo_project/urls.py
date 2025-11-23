from django.contrib import admin
from django.urls import path
from todos import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("add/", views.add_todo, name="add_todo"),
    # The <int:todo_id> part captures the ID from the URL (e.g. /delete/1/)
    path("delete/<int:todo_id>/", views.delete_todo, name="delete_todo"),
    path("toggle/<int:todo_id>/", views.toggle_todo, name="toggle_todo"),
]
