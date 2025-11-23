from django.test import TestCase, Client
from django.urls import reverse
from .models import Todo


class TodoTests(TestCase):
    def setUp(self):
        # Create a sample todo for testing
        self.todo = Todo.objects.create(title="Test Task")
        self.client = Client()

    def test_model_content(self):
        # Does the model save correctly?
        self.assertEqual(self.todo.title, "Test Task")
        self.assertFalse(self.todo.is_resolved)

    def test_homepage(self):
        # Does the homepage load?
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")

    def test_add_todo(self):
        # Can we add a new task via the form?
        response = self.client.post(reverse("add_todo"), {"title": "New Entry"})
        # Should redirect back home (302)
        self.assertEqual(response.status_code, 302)
        # Should be 2 items in DB now
        self.assertEqual(Todo.objects.count(), 2)
