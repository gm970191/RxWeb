import logging
import os
import smtplib
from email.message import EmailMessage

_logger = logging.getLogger("rxweb.mail")


def public_base_url(request) -> str:
    configured = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
    if configured:
        return configured
    return str(request.base_url).rstrip("/")


def send_email(to_addr: str, subject: str, text_body: str) -> bool:
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host or not to_addr:
        return False
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASS", "").strip()
    from_addr = os.environ.get("SMTP_FROM", user or "noreply@localhost")
    use_ssl = os.environ.get("SMTP_SSL", "").strip() in ("1", "true", "True")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(text_body)

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls()
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        return True
    except Exception as exc:
        _logger.warning("发送邮件失败: %s", exc)
        return False
