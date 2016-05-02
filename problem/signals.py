from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .models import GroupProfile
#  from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, remove_perm
from .models import Problem


def change_perm(func, instance, pk_set):
    if not pk_set:
        return
    ancestors = set()
    descendants = set()
    groups = GroupProfile.objects.filter(pk__in=pk_set)
    #  print ancestors, descendants
    #  here should use cache,  all of  anc,admin,des
    for group in groups:
        ancestors.update(group.get_ancestors(include_self=True))
        descendants.update(group.get_descendants(include_self=True))
    for ans in ancestors:
        func('ojuser.change_problem', ans.admin_group, instance)
        func('ojuser.change_problem', ans.superadmin, instance)
        func('ojuser.view_problem', ans.admin_group, instance)
        func('ojuser.view_problem', ans.superadmin, instance)
    for des in descendants:
        func('ojuser.view_problem', des.user_group, instance)


@receiver(m2m_changed, sender=Problem.groups.through)
def handle_problem_group_save(sender, instance, action, pk_set, reverse, **kwargs):
    print instance, action, pk_set, reverse
    if action == "post_add" and not reverse:
        change_perm(assign_perm, instance, pk_set)
    elif action == "post_clear" and not reverse:
        change_perm(remove_perm, instance, pk_set)


@receiver(post_save, sender=Problem)
def handle_problem_save(sender, instance, created, **kwargs):
    if created:
        assign_perm('ojuser.delete_problem', instance.superadmin, instance)
