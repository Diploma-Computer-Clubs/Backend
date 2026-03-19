from fastapi.concurrency import run_in_threadpool
from twilio.base.exceptions import TwilioRestException

from src.shared.configurations.config import settings, get_twilio


async def send_sms_via_twilio(to_number: str, body: str):
    try:
        client = get_twilio()
        message = await run_in_threadpool(
            client.messages.create,
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return True

    except TwilioRestException as e:
        print(f"Error Twilio (wrong number): {e.msg}")
        return False
    except Exception as e:
        print(f"Invalid Error: {e}")
        return False
