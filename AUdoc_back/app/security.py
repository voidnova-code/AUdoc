"""
Security utilities for the AUdoc application.

This module provides:
- Rate limiting decorators to prevent brute force attacks
- Secure token generation and validation
- Input sanitization helpers
- Security logging
"""

import hashlib
import hmac
import logging
import re
import secrets
import time
from functools import wraps
from typing import Any, Callable, Optional

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest

logger = logging.getLogger("app.security")


# ══════════════════════════════════════════════════════════════════════════════
#  RATE LIMITING
# ══════════════════════════════════════════════════════════════════════════════

def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.
    Handles X-Forwarded-For header for proxied requests.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (client's real IP)
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip


def rate_limit(
    key_prefix: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    per_user: bool = False,
    error_message: str = "Too many requests. Please try again later.",
):
    """
    Rate limiting decorator for views.
    
    Args:
        key_prefix: Unique prefix for the rate limit key
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
        per_user: If True, rate limit per user instead of per IP
        error_message: Message to return when rate limit is exceeded
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            # Build the rate limit key
            if per_user and request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
            else:
                identifier = f"ip:{get_client_ip(request)}"
            
            cache_key = f"ratelimit:{key_prefix}:{identifier}"
            
            # Get current request count and window start
            rate_data = cache.get(cache_key, {"count": 0, "window_start": time.time()})
            
            # Check if we're in a new window
            current_time = time.time()
            if current_time - rate_data["window_start"] > window_seconds:
                # Reset the window
                rate_data = {"count": 0, "window_start": current_time}
            
            # Check if rate limit exceeded
            if rate_data["count"] >= max_requests:
                remaining_time = int(window_seconds - (current_time - rate_data["window_start"]))
                logger.warning(
                    f"Rate limit exceeded for {identifier} on {key_prefix}. "
                    f"Requests: {rate_data['count']}/{max_requests}"
                )
                return JsonResponse(
                    {
                        "error": error_message,
                        "retry_after": remaining_time,
                    },
                    status=429,
                )
            
            # Increment request count
            rate_data["count"] += 1
            cache.set(cache_key, rate_data, timeout=window_seconds)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit_otp(view_func: Callable) -> Callable:
    """Rate limit decorator specifically for OTP endpoints."""
    config = getattr(settings, "RATE_LIMIT_OTP", {"max_requests": 5, "window_seconds": 300})
    return rate_limit(
        key_prefix="otp",
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        error_message="Too many OTP requests. Please wait 5 minutes before trying again.",
    )(view_func)


def rate_limit_login(view_func: Callable) -> Callable:
    """Rate limit decorator specifically for login endpoints."""
    config = getattr(settings, "RATE_LIMIT_LOGIN", {"max_requests": 10, "window_seconds": 300})
    return rate_limit(
        key_prefix="login",
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        error_message="Too many login attempts. Please wait 5 minutes before trying again.",
    )(view_func)


def rate_limit_api(view_func: Callable) -> Callable:
    """Rate limit decorator for general API endpoints."""
    config = getattr(settings, "RATE_LIMIT_API", {"max_requests": 100, "window_seconds": 60})
    return rate_limit(
        key_prefix="api",
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        per_user=True,
        error_message="API rate limit exceeded. Please slow down your requests.",
    )(view_func)


# ══════════════════════════════════════════════════════════════════════════════
#  OTP SECURITY
# ══════════════════════════════════════════════════════════════════════════════

def generate_secure_otp(length: int = 6) -> str:
    """
    Generate a cryptographically secure OTP.
    Uses secrets module for secure random number generation.
    """
    # Generate OTP using secrets for cryptographic security
    max_value = 10 ** length - 1
    min_value = 10 ** (length - 1)
    return str(secrets.randbelow(max_value - min_value + 1) + min_value)


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings using constant-time comparison to prevent timing attacks.
    """
    return hmac.compare_digest(val1, val2)


def hash_otp(otp: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash an OTP for secure storage.
    Returns (hash, salt) tuple.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 for OTP hashing
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        otp.encode(),
        salt.encode(),
        100000,  # iterations
    )
    return hash_bytes.hex(), salt


def verify_otp_hash(otp: str, stored_hash: str, salt: str) -> bool:
    """
    Verify an OTP against its stored hash using constant-time comparison.
    """
    computed_hash, _ = hash_otp(otp, salt)
    return constant_time_compare(computed_hash, stored_hash)


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT VALIDATION & SANITIZATION
# ══════════════════════════════════════════════════════════════════════════════

def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input by stripping whitespace and limiting length.
    Note: Django's ORM already escapes SQL. This is for additional safety.
    """
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def validate_student_id(student_id: str) -> bool:
    """
    Validate student ID format.
    Expected format: alphanumeric, 5-50 characters.
    """
    if not student_id:
        return False
    # Alphanumeric with possible hyphens/underscores
    pattern = r"^[A-Za-z0-9_-]{5,50}$"
    return bool(re.match(pattern, student_id))


def validate_email_format(email: str) -> bool:
    """
    Basic email format validation.
    Django's EmailField provides thorough validation, this is a quick check.
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    Allows digits, spaces, hyphens, and parentheses.
    """
    if not phone:
        return False
    # Remove formatting characters
    digits_only = re.sub(r"[\s\-\(\)\+]", "", phone)
    # Should be 10-15 digits
    return len(digits_only) >= 10 and len(digits_only) <= 15 and digits_only.isdigit()


# ══════════════════════════════════════════════════════════════════════════════
#  SECURE TOKEN GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    Uses secrets module for cryptographic security.
    """
    return secrets.token_urlsafe(length)


def generate_confirmation_token() -> str:
    """
    Generate a secure token for email confirmation links.
    """
    return secrets.token_urlsafe(48)


# ══════════════════════════════════════════════════════════════════════════════
#  SECURITY LOGGING
# ══════════════════════════════════════════════════════════════════════════════

def log_security_event(
    event_type: str,
    request: HttpRequest,
    details: Optional[dict] = None,
    level: str = "warning",
):
    """
    Log a security-related event.
    
    Args:
        event_type: Type of security event (e.g., "failed_login", "rate_limit")
        request: The HTTP request
        details: Additional details to log
        level: Log level (info, warning, error)
    """
    ip = get_client_ip(request)
    user_id = request.user.id if request.user.is_authenticated else None
    
    log_data = {
        "event": event_type,
        "ip": ip,
        "user_id": user_id,
        "path": request.path,
        "method": request.method,
    }
    
    if details:
        log_data.update(details)
    
    message = f"Security Event: {event_type} | IP: {ip} | Path: {request.path}"
    if details:
        message += f" | Details: {details}"
    
    log_func = getattr(logger, level, logger.warning)
    log_func(message)


def log_failed_login(request: HttpRequest, identifier: str, reason: str = ""):
    """Log a failed login attempt."""
    log_security_event(
        "failed_login",
        request,
        {"identifier": identifier, "reason": reason},
        level="warning",
    )


def log_suspicious_activity(request: HttpRequest, activity: str, details: Optional[dict] = None):
    """Log suspicious activity for review."""
    log_security_event(
        "suspicious_activity",
        request,
        {"activity": activity, **(details or {})},
        level="warning",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  API AUTHENTICATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def require_authenticated_api(view_func: Callable) -> Callable:
    """
    Decorator to require authentication for API endpoints.
    Returns 401 Unauthorized if not authenticated.
    """
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401,
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def require_staff_api(view_func: Callable) -> Callable:
    """
    Decorator to require staff/admin authentication for API endpoints.
    Returns 403 Forbidden if not staff.
    """
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401,
            )
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse(
                {"error": "Staff access required"},
                status=403,
            )
        return view_func(request, *args, **kwargs)
    return wrapper
