import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.appointment_notifications import AppointmentReminder, send_appointment_reminder
from src.infrai_email import InfraiEmail


destination = os.environ["DEMO_EMAIL_TO"]
reminder = AppointmentReminder(
    patient_email=destination,
    patient_name="Alex",
    appointment_id="demo-appointment-001",
    appointment_time="2026-11-05 09:30",
    clinic_name="Harbor Health",
)
print(send_appointment_reminder(reminder, InfraiEmail()))
