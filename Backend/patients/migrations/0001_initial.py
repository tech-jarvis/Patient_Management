import django.db.models.deletion
import django.utils.timezone
import patients.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    default=False,
                    help_text='Designates that this user has all permissions without explicitly assigning them.',
                    verbose_name='superuser status',
                )),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(
                    default=False,
                    help_text='Designates whether the user can log into this admin site.',
                    verbose_name='staff status',
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Designates whether this user should be treated as active.',
                    verbose_name='active',
                )),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('groups', models.ManyToManyField(
                    blank=True,
                    help_text='The groups this user belongs to.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.group',
                    verbose_name='groups',
                )),
                ('user_permissions', models.ManyToManyField(
                    blank=True,
                    help_text='Specific permissions for this user.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.permission',
                    verbose_name='user permissions',
                )),
            ],
            options={
                'verbose_name': 'clinic',
                'verbose_name_plural': 'clinics',
                'abstract': False,
            },
            managers=[
                ('objects', patients.models.ClinicManager()),
            ],
        ),
        migrations.CreateModel(
            name='Clinician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('specialization', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clinic', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='clinicians',
                    to='patients.clinic',
                )),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(
                        fields=['clinic', 'email'],
                        condition=models.Q(email__gt=''),
                        name='unique_clinician_email_per_clinic',
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('email', models.EmailField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clinic', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='patients',
                    to='patients.clinic',
                )),
            ],
            options={
                'ordering': ['-created_at'],
                'constraints': [
                    models.UniqueConstraint(
                        fields=['clinic', 'email'],
                        condition=models.Q(email__gt=''),
                        name='unique_patient_email_per_clinic',
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_at', models.DateTimeField()),
                ('duration_minutes', models.PositiveIntegerField(default=30)),
                ('status', models.CharField(
                    choices=[
                        ('scheduled', 'Scheduled'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                        ('no_show', 'No Show'),
                    ],
                    default='scheduled',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='appointments',
                    to='patients.patient',
                )),
            ],
            options={
                'ordering': ['-scheduled_at'],
            },
        ),
        migrations.CreateModel(
            name='AppointmentClinician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='appointment_clinicians',
                    to='patients.appointment',
                )),
                ('clinician', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='appointment_clinicians',
                    to='patients.clinician',
                )),
            ],
            options={
                'unique_together': {('appointment', 'clinician')},
            },
        ),
    ]
