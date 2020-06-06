from phone_verify.services import PhoneVerificationService, get_sms_backend

import logging

logger = logging.getLogger(__name__)


def send_security_code(phone_number):
    sms_backend = get_sms_backend(phone_number)
    security_code, session_token = sms_backend\
        .create_security_code_and_session_token(phone_number)

    service = PhoneVerificationService(phone_number=phone_number)

    try:
        service.send_verification(phone_number, security_code)
    except service.backend.exception_class as exc:
        logger.error(
            "Error in sending verification code to {phone_number}: "
            "{error}".format(phone_number=phone_number, error=exc)
        )
        raise exc

    return session_token
