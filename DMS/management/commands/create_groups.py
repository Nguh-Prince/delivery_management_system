# core/management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **kwargs):
        # Define groups and their permissions
        groups_permissions = {
            'Clients': ['can_make_orders', 'can_view_cart', 'can_add_to_cart', 'can_get_articles_delivered', 'can_decline_orders'],
            'Couriers': ['can_view_deliveries', 'can_manage_deliveries'],
            'Storekeepers': ['can_manage_articles', 'can_notify_courier'],
            'Admins': [
                'can_manage_couriers', 'can_manage_storekeepers', 'can_manage_clients',
                'can_view_overall_info', 'can_manage_articles', 'can_notify_courier',
                'can_manage_refunds', 'can_view_deliveries', 'can_manage_deliveries'
            ],
        }

        # Create groups and assign permissions
        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm in permissions:
                permission = Permission.objects.get(codename=perm)
                group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS('Successfully created groups and assigned permissions'))
