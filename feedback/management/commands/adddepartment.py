from django.core.management.base import BaseCommand, CommandError
from feedback.models import Department

class Command(BaseCommand):
    help = "Add a new department to the system"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the department to add")
        parser.add_argument("--description", type=str, help="Description of the department", default="")

    def handle(self, *args, **options):
        name = options["name"]
        description = options["description"]

        if Department.objects.filter(name=name).exists():
            raise CommandError(f"Department with name '{name}' already exists.")
        department = Department(name=name, description=description)
        department.save()

        self.stdout.write(self.style.SUCCESS(f"Department '{name}' added successfully."))