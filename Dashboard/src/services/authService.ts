import api from '../api/client';
import type { AuthResponse, LoginPayload, UserProfile } from '../types';

export const authService = {
  login: (payload: LoginPayload) => api.post<AuthResponse>('/auth/login', payload),
  me: () => api.get<UserProfile>('/auth/me')
};
