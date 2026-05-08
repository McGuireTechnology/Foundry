# Authentication

This document summarizes the current authentication experience implemented in `apps/web` and `apps/api`.

## Overview

Foundry now supports a full primitive auth flow with dedicated pages:

- `/signin`
- `/signup`
- `/signout`
- `/forgot-password`
- `/dashboard` (post-login landing route)

Auth pages use a dedicated layout and branding treatment distinct from the main dashboard shell.

## Identity Model

Foundry uses **email as the user identity** for authentication requests:

- Sign up payload: `email`, `password`
- Sign in payload: `email`, `password`

## Sign Up Flow

From `/signup`, users can create an account with email and password.

Behavior:

- On success: redirect to `/signin` with:
  - prefilled email
  - account-created success notice
- On duplicate email (`409`): user-friendly guidance to sign in or use a different email.
- Enter key submits the form (same as clicking **Create Account**).
- Request timeout handling avoids UI lock-up when backend is unreachable.

## Sign In Flow

From `/signin`, users authenticate with email and password.

Behavior:

- On success: tokens stored in local storage and redirect to:
  - `next` query target when present and internal, otherwise
  - `/dashboard`
- Enter key submits the form (same as clicking **Sign In**).
- `Remember me` stores the most recent successful email for future prefill.
- Friendly notices include:
  - account created (from sign-up redirect)
  - session expired (from 401 redirect nuance)

## Sign Out Flow

From `/signout`, auth tokens are cleared and user receives confirmation.

Behavior:

- Sign-out clears stored auth tokens immediately on page load.
- A single explicit in-page confirmation message is shown:
  - "You have been signed out."
- Redundant global auth banner messaging is intentionally avoided on this route to reduce duplicated notifications.

## Forgot Password (Primitive)

From `/signin`, users can navigate to `/forgot-password`.

Behavior:

- Submit email to `POST /auth/forgot-password`
- Always returns a generic success message:
  - "If an account exists for that email, password reset instructions will be sent."
- Does not reveal whether an account exists for the email.

This is currently a primitive request-only flow (no reset token completion UI yet).

## 401 Handling and Session Nuance

The frontend includes shared API behavior for `401 Unauthorized` responses:

- Redirect to `/signin?next=<current-path>` by default.
- If a token existed locally at time of `401`, treat it as likely expired session:
  - clear auth state
  - redirect to `/signin?next=<current-path>&expired=1`
  - sign-in screen displays: "Your session expired. Please sign in again."

## API Endpoints Used

- `POST /users` - create account
- `POST /auth/token` - sign in and issue tokens
- `POST /auth/refresh` - refresh tokens
- `POST /auth/forgot-password` - primitive reset request

All auth-related frontend requests send `X-API-Version: v1`.

## Local Development CORS

For local web-to-api auth calls (for example, `http://localhost:5173` -> `http://localhost:8000/auth/token`), API CORS is configured to allow:

- Explicit origins from env config (`CORS_ALLOW_ORIGINS` / `BACKEND_CORS_ORIGINS`)
- A localhost regex fallback for local dev hosts:
  - `localhost` and `127.0.0.1` across ports

## UX and Branding Notes

- Auth pages include the same two-column Foundry wordmark treatment as the main app shell.
- Header auth actions are contextual:
  - signed out: show sign-in/sign-up actions
  - signed in: show sign-out action

## Current Limitations

- No completed password-reset token flow yet (request-only stage).
- No silent refresh lifecycle for access token expiry yet.
- No auth route guard matrix beyond existing redirect behavior.
