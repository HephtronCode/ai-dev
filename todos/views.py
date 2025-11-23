"""Views for the todos app providing list, create, delete and toggle actions."""

try:
    from django.shortcuts import render, redirect, get_object_or_404
except ImportError:  # pragma: no cover - provide stubs when Django is not available
    def render(_request, _template_name, context=None):
        """Stub render used when Django is not available; returns None."""
        del _request, _template_name, context
        return None

    def redirect(_to, *args, **kwargs):
        """Stub redirect used when Django is not available; returns None."""
        del _to, args, kwargs
        return None

    class _DoesNotExist(Exception):
        """Internal exception used by the stub get_object_or_404."""
        pass

    def get_object_or_404(_model, *args, **kwargs):
        """Stub get_object_or_404 that always raises _DoesNotExist when Django is not available."""
        del _model, args, kwargs
        raise _DoesNotExist

from .models import Todo


def home(request):
    """Render the home page with all todos ordered by due date."""
    todos = Todo.objects.all().order_by("due_date")
    return render(request, "home.html", {"todos": todos})


def add_todo(request):
    """Create a new todo when POSTing a title, then redirect to home."""
    if request.method == "POST":
        title = request.POST.get("title")
        if title:
            Todo.objects.create(title=title)
    return redirect("home")


def delete_todo(request, todo_id):
    """Delete the todo identified by todo_id and redirect to home."""
    _ = request
    todo = get_object_or_404(Todo, id=todo_id)
    todo.delete()
    return redirect("home")


def toggle_todo(request, todo_id):
    """Toggle the resolved state of the todo identified by todo_id."""
    _ = request
    todo = get_object_or_404(Todo, id=todo_id)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    return redirect("home")
