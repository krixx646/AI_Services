from django.core.exceptions import ValidationError
from django.conf import settings


def _domain_matches(disposable_set, domain: str) -> bool:
    domain = domain.lower().strip('.')
    # direct match
    if domain in disposable_set:
        return True
    # subdomain match
    parts = domain.split('.')
    for i in range(1, len(parts)):
        candidate = '.'.join(parts[i:])
        if candidate in disposable_set:
            return True
    # wildcard suffix entries like *.tempmail.com
    for entry in disposable_set:
        if entry.startswith('*.') and domain.endswith(entry[2:]):
            return True
    return False


def validate_not_disposable_email(value: str) -> str:
    """Raise ValidationError if email is disposable/temporary or obviously dummy.

    Uses DISPOSABLE_EMAIL_DOMAINS and BANNED_EMAIL_LOCALPARTS from settings.
    """
    if not value or '@' not in value:
        raise ValidationError("Enter a valid email address.")

    local, domain = value.rsplit('@', 1)
    local = local.strip().lower()
    domain = domain.strip().lower()

    banned_locals = set(getattr(settings, 'BANNED_EMAIL_LOCALPARTS', set()))
    if local in banned_locals:
        raise ValidationError("Enter a real email address (not a placeholder like 'test').")

    disposable_set = set(getattr(settings, 'DISPOSABLE_EMAIL_DOMAINS', set()))
    if _domain_matches(disposable_set, domain):
        raise ValidationError("Disposable or temporary email domains are not allowed.")

    return value


