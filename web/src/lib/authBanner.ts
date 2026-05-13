const AUTH_BANNER_KEY = "vortex.auth_banner";

export function setAuthBanner(message: string): void {
  sessionStorage.setItem(AUTH_BANNER_KEY, message);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("vortex-auth-banner"));
  }
}

export function popAuthBanner(): string {
  const value = sessionStorage.getItem(AUTH_BANNER_KEY) ?? "";
  if (value) {
    sessionStorage.removeItem(AUTH_BANNER_KEY);
  }
  return value;
}
