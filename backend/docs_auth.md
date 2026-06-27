# JWT Authentication

## Register

```http
POST /api/v1/auth/register
Content-Type: application/json
```

```json
{
  "email": "demo@example.com",
  "username": "demo",
  "password": "Passw0rd!"
}
```

## Login

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "demo@example.com",
  "password": "Passw0rd!"
}
```

Response:

```json
{
  "access_token": "xxx.yyy.zzz",
  "token_type": "bearer",
  "expires_in": 86400
}
```

## Protected Request

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Implementation Notes

- Password hashing uses PBKDF2-SHA256.
- JWT uses HS256.
- `SECRET_KEY` must be changed in production.
- Disabled users cannot access protected routes.
