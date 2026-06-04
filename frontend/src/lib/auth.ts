// Token persistence. Single source for the localStorage key so nothing else
// hardcodes it. Phase F2 uses localStorage (XSS-exposed but simple) as planned.
const TOKEN_KEY = "tracepilot_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}
