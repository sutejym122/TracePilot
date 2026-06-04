// Thin typed wrappers over the auth endpoints. No React here.
import { apiGet, apiPost } from "../lib/apiClient";
import type {
  LoginPayload,
  RegisterPayload,
  RegisterResponse,
  TokenResponse,
  User,
} from "../types/auth";

export const authApi = {
  register: (payload: RegisterPayload) =>
    apiPost<RegisterResponse>("/api/auth/register", payload),
  login: (payload: LoginPayload) =>
    apiPost<TokenResponse>("/api/auth/login", payload),
  me: () => apiGet<User>("/api/users/me"),
};
