from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AppointmentReminder:
    patient_email: str
    patient_name: str
    appointment_id: str
    appointment_time: str
    clinic_name: str


class EmailGateway(Protocol):
    def is_suppressed(self, email: str) -> bool: ...
    def send(self, to: str, subject: str, body: str) -> Any: ...


def send_appointment_reminder(appointment: AppointmentReminder, gateway: EmailGateway) -> dict[str, Any]:
    if gateway.is_suppressed(appointment.patient_email):
        return {"decision": "suppressed", "appointment_id": appointment.appointment_id}

    result = gateway.send(
        appointment.patient_email,
        f"Appointment reminder for {appointment.clinic_name}",
        (
            f"Hello {appointment.patient_name}, your appointment at {appointment.clinic_name} "
            f"is scheduled for {appointment.appointment_time}. Appointment ID: {appointment.appointment_id}."
        ),
    )
    return {"decision": "sent", "appointment_id": appointment.appointment_id, "message": result}
