// Mirrors the backend auth response shapes exactly. Dates are ISO strings.
export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// /api/auth/register returns the user fields AND a token in one response.
export interface RegisterResponse extends User {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}
