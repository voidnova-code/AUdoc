# Security Documentation for AUdoc

This document outlines the security measures implemented in the AUdoc Campus Health application.

## Security Features

### 1. Authentication & Authorization

- **OTP-based Login**: Students authenticate using One-Time Passwords sent via email
- **Rate Limiting**: Protection against brute force attacks
  - OTP endpoints: 5 requests per 5 minutes
  - Login endpoints: 10 requests per 5 minutes
  - API endpoints: 100 requests per minute per user
- **Session Security**: Secure cookie configuration with HttpOnly and SameSite flags
- **Staff/Admin Separation**: Role-based access control for admin functions

### 2. Data Protection

- **No Raw SQL**: All database operations use Django ORM (parameterized queries)
- **Input Sanitization**: All user inputs are sanitized and length-limited
- **Constant-Time Comparison**: OTP verification uses timing-attack resistant comparison
- **Secure OTP Generation**: Cryptographically secure random number generation

### 3. Web Security Headers

- **X-Frame-Options**: DENY (clickjacking protection)
- **X-Content-Type-Options**: nosniff
- **X-XSS-Protection**: Enabled
- **Strict-Transport-Security**: HSTS enabled in production
- **Referrer-Policy**: strict-origin-when-cross-origin

### 4. CSRF Protection

- **CSRF Tokens**: Required for all state-changing operations
- **Admin Actions**: Changed from GET to POST to prevent CSRF attacks
- **API Endpoints**: Rate-limited to mitigate abuse (CSRF exempt for Flutter app)

### 5. Session Security

```python
SESSION_COOKIE_SECURE = True       # HTTPS only (production)
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
SESSION_COOKIE_SAMESITE = "Lax"    # CSRF protection
CSRF_COOKIE_SECURE = True          # HTTPS only (production)
CSRF_COOKIE_HTTPONLY = True        # No JavaScript access
```

### 6. Password Security

- **Argon2 Hashing**: Primary password hasher (memory-hard)
- **Strong Validators**: Length, common password, numeric-only checks
- **Students**: No password stored (OTP-only authentication)

## Configuration Checklist

### Production Deployment

1. **Set Environment Variables**:
   ```bash
   DJANGO_SECRET_KEY=<strong-random-key>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=yourdomain.com
   DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   DJANGO_SECURE_SSL_REDIRECT=True
   ```

2. **Enable HTTPS**: Use a valid SSL/TLS certificate

3. **Database**: Use PostgreSQL instead of SQLite for production

4. **Review Logs**: Monitor `logs/security.log` for suspicious activity

## Security Logging

Security events are logged to `logs/security.log`:

- Failed login attempts
- Rate limit violations
- OTP verification failures
- Suspicious activities

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do not** disclose publicly until fixed
2. Email the development team with details
3. Include steps to reproduce if possible

## Dependencies Security

Keep dependencies updated:

```bash
pip install --upgrade -r requirements.txt
pip install pip-audit
pip-audit  # Check for known vulnerabilities
```

## API Security

### Rate Limiting

All API endpoints are rate-limited:

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| OTP Send | 5 | 5 minutes |
| Login | 10 | 5 minutes |
| General API | 100 | 1 minute |

### Authentication

- Session-based authentication for web
- OTP verification required for Flutter app
- No sensitive data in URLs

## Best Practices Followed

1. ✅ No hardcoded secrets (use environment variables)
2. ✅ Parameterized queries (Django ORM)
3. ✅ Input validation and sanitization
4. ✅ Secure session management
5. ✅ Rate limiting on sensitive endpoints
6. ✅ Security headers configured
7. ✅ CSRF protection enabled
8. ✅ Secure password hashing (Argon2)
9. ✅ Timing-attack resistant OTP comparison
10. ✅ Security event logging
