from src.appointment_notifications import AppointmentReminder, send_appointment_reminder


class SuppressionGateway:
    def __init__(self) -> None:
        self.sent = False

    def is_suppressed(self, email: str) -> bool:
        return email == "patient@example.com"

    def send(self, to: str, subject: str, body: str) -> dict[str, str]:
        self.sent = True
        return {"message_id": "unexpected"}


def test_hard_bounced_patient_does_not_receive_another_reminder() -> None:
    gateway = SuppressionGateway()
    appointment = AppointmentReminder("patient@example.com", "Mina", "apt-42", "2026-11-05 09:30", "Harbor Health")

    result = send_appointment_reminder(appointment, gateway)

    assert result == {"decision": "suppressed", "appointment_id": "apt-42"}
    assert gateway.sent is False
