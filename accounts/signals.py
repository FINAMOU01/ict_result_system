from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_login_failed
from accounts.models import CustomUser, ActivityLog
from academics.models import Semester, Course, Enrollment


def log_activity(user, action, description, affected_entity='', ip_address=None, status='success'):
    """Helper function to log an activity"""
    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        affected_entity=affected_entity,
        ip_address=ip_address,
        status=status
    )


# CustomUser signals
@receiver(post_save, sender=CustomUser)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user creation or updates"""
    if created:
        log_activity(
            user=None,  # System action
            action='user_create',
            description=f"User account created for {instance.get_full_name()} ({instance.username}) with role: {instance.get_role_display()}",
            affected_entity=f"User: {instance.username}"
        )
    else:
        log_activity(
            user=None,  # System action
            action='user_update',
            description=f"User {instance.username} ({instance.get_full_name()}) profile updated",
            affected_entity=f"User: {instance.username}"
        )


# Semester signals
@receiver(post_save, sender=Semester)
def log_semester_changes(sender, instance, created, **kwargs):
    """Log semester creation or updates"""
    if created:
        log_activity(
            user=None,
            action='semester_create',
            description=f"Semester '{instance.name}' (Academic Year: {instance.academic_year}) created - Status: {'Active' if instance.is_active else 'Inactive'}",
            affected_entity=f"Semester: {instance.name}"
        )
    else:
        log_activity(
            user=None,
            action='semester_update',
            description=f"Semester '{instance.name}' updated - Academic Year: {instance.academic_year}, Status: {'Active' if instance.is_active else 'Inactive'}",
            affected_entity=f"Semester: {instance.name}"
        )


@receiver(post_delete, sender=Semester)
def log_semester_delete(sender, instance, **kwargs):
    """Log semester deletion"""
    log_activity(
        user=None,
        action='semester_delete',
        description=f"Semester '{instance.name}' (Academic Year: {instance.academic_year}) was deleted",
        affected_entity=f"Semester: {instance.name}"
    )


# Course signals
@receiver(post_save, sender=Course)
def log_course_changes(sender, instance, created, **kwargs):
    """Log course creation or updates"""
    if created:
        log_activity(
            user=None,
            action='course_create',
            description=f"Course '{instance.name}' (Code: {instance.code}) created in semester {instance.semester.name}",
            affected_entity=f"Course: {instance.code}"
        )
    else:
        log_activity(
            user=None,
            action='course_update',
            description=f"Course '{instance.name}' (Code: {instance.code}) updated",
            affected_entity=f"Course: {instance.code}"
        )


@receiver(post_delete, sender=Course)
def log_course_delete(sender, instance, **kwargs):
    """Log course deletion"""
    log_activity(
        user=None,
        action='course_delete',
        description=f"Course '{instance.name}' (Code: {instance.code}) was deleted",
        affected_entity=f"Course: {instance.code}"
    )


# Enrollment signals
@receiver(post_save, sender=Enrollment)
def log_enrollment_changes(sender, instance, created, **kwargs):
    """Log enrollment creation"""
    if created:
        log_activity(
            user=None,
            action='enrollment_create',
            description=f"Student {instance.student.matricule} enrolled in course {instance.course.code} ({instance.course.name})",
            affected_entity=f"Enrollment: {instance.student.matricule} - {instance.course.code}"
        )


@receiver(post_delete, sender=Enrollment)
def log_enrollment_delete(sender, instance, **kwargs):
    """Log enrollment deletion"""
    log_activity(
        user=None,
        action='enrollment_delete',
        description=f"Student {instance.student.matricule} removed from course {instance.course.code}",
        affected_entity=f"Enrollment: {instance.student.matricule} - {instance.course.code}"
    )
