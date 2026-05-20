from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Create default groups and sample users for testing'

    def handle(self, *args, **options):
        for name in ['Admin', 'Faculty', 'Student']:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{name}" created'))
            else:
                self.stdout.write(f'Group "{name}" already exists')

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@school.edu',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.groups.add(Group.objects.get(name='Admin'))
        self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))

        faculty_user, _ = User.objects.get_or_create(
            username='faculty',
            defaults={'email': 'faculty@school.edu'}
        )
        faculty_user.set_password('faculty123')
        faculty_user.save()
        faculty_user.groups.add(Group.objects.get(name='Faculty'))
        self.stdout.write(self.style.SUCCESS('Faculty user created: faculty / faculty123'))

        student_user, _ = User.objects.get_or_create(
            username='student',
            defaults={'email': 'student@school.edu'}
        )
        student_user.set_password('student123')
        student_user.save()
        student_user.groups.add(Group.objects.get(name='Student'))
        self.stdout.write(self.style.SUCCESS('Student user created: student / student123'))
