const ACCESS_TOKEN_KEY = "vortex.access_token";
const REFRESH_TOKEN_KEY = "vortex.refresh_token";
const REMEMBERED_EMAIL_KEY = "vortex.remembered_email";
const CURRENT_USER_EMAIL_KEY = "vortex.current_user_email";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
};

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function storeTokens(tokens: TokenPair): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("vortex-auth-changed"));
  }
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(CURRENT_USER_EMAIL_KEY);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("vortex-auth-changed"));
  }
}

export function hasAccessToken(): boolean {
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
}

export function getAccessToken(): string {
  return localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
}

export function getRefreshToken(): string {
  return localStorage.getItem(REFRESH_TOKEN_KEY) ?? "";
}

export function getRememberedEmail(): string {
  return localStorage.getItem(REMEMBERED_EMAIL_KEY) ?? "";
}

export function rememberEmail(email: string): void {
  localStorage.setItem(REMEMBERED_EMAIL_KEY, email.trim());
}

export function clearRememberedEmail(): void {
  localStorage.removeItem(REMEMBERED_EMAIL_KEY);
}

export function setCurrentUserEmail(email: string): void {
  localStorage.setItem(CURRENT_USER_EMAIL_KEY, email.trim());
}

export function getCurrentUserEmail(): string {
  return localStorage.getItem(CURRENT_USER_EMAIL_KEY) ?? "";
}
