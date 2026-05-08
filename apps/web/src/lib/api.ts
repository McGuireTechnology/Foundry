import { apiBaseUrl, clearTokens, getRefreshToken, hasAccessToken, storeTokens } from "./auth";
import { setAuthBanner } from "./authBanner";

type ApiFetchOptions = {
  redirectOn401?: boolean;
};

export async function apiFetch(
  path: string,
  init?: RequestInit,
  options: ApiFetchOptions = {}
): Promise<Response> {
  const { redirectOn401 = true } = options;
  let response = await fetch(`${apiBaseUrl}${path}`, init);

  if (response.status === 401 && hasAccessToken()) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      response = await fetch(`${apiBaseUrl}${path}`, init);
    }
  }

  if (response.status === 401 && redirectOn401 && typeof window !== "undefined") {
    const hadToken = hasAccessToken();
    if (hadToken) {
      clearTokens();
      setAuthBanner("Your session expired. Please sign in again.");
    }

    const currentPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    const query = new URLSearchParams({ next: currentPath });
    if (hadToken) {
      query.set("expired", "1");
    }
    const signinPath = `/signin?${query.toString()}`;
    if (!window.location.pathname.startsWith("/signin")) {
      window.location.assign(signinPath);
    }
  }

  return response;
}

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(`${apiBaseUrl}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Version": "v1"
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (!response.ok) {
      return false;
    }

    const tokens = (await response.json()) as { access_token: string; refresh_token: string };
    storeTokens(tokens);
    return true;
  } catch {
    return false;
  }
}
