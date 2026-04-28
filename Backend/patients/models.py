from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class ClinicManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)


class Clinic(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = ClinicManager()

    class Meta:
        verbose_name = 'clinic'
        verbose_name_plural = 'clinics'

    def __str__(self):
        return self.name


class Clinician(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name='clinicians')
    name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['clinic', 'email'],
                condition=models.Q(email__gt=''),
                name='unique_clinician_email_per_clinic',
            )
        ]

    def __str__(self):
        return self.name


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patients')
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['clinic', 'email'],
                condition=models.Q(email__gt=''),
                name='unique_patient_email_per_clinic',
            )
        ]

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.patient.name} — {self.scheduled_at:%Y-%m-%d %H:%M}"


class AppointmentClinician(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='appointment_clinicians')
    clinician = models.ForeignKey(Clinician, on_delete=models.CASCADE, related_name='appointment_clinicians')

    class Meta:
        unique_together = [('appointment', 'clinician')]

    def __str__(self):
        return f"{self.appointment} — {self.clinician.name}"
