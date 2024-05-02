import logging

from fastapi import APIRouter

from mail.emailService import send_email

router = APIRouter(prefix="/_test", tags=["_test"])


@router.get("/email/{to}/{subject}/{content}")
async def test_email_router(to: str, subject: str, content: str):
    """ Testing the email connection and send email function. """
    logging.info(f"Testing router {to}/{subject}/{content}")

    response = await send_email(to, subject, content)

    if response:
        logging.info(f"Successfully sent email to {to}/{subject}/{content}")
        return response
    else:
        logging.error(f"Failed to send email to {to}/{subject}/{content}")
        return response
