import type { User } from './api-types';

/**
 * Payload used for registering a new user.
 *
 * Example:
 * const data: UserRegistration = {
 *   email: "user@example.com",
 *   password: "strongpassword",
 *   displayName: "Harsh"
 * };
 */
export interface UserRegistration {
  email: string;
  password: string;
  displayName: string;
}

/**
 * Payload used for logging in an existing user.
 *
 * Example:
 * const data: UserLogin = {
 *   email: "user@example.com",
 *   password: "mypassword"
 * };
 */
export interface UserLogin {
  email: string;
  password: string;
}

/**
 * Authentication response returned after successful login or registration.
 *
 * Example:
 * const auth: AuthResponse = {
 *   token: "jwt-token",
 *   user: { ...userObject },
 *   expiresIn: 3600
 * };
 */
export interface AuthResponse {
  token: string;
  user: User;
  expiresIn: number;
}

/**
 * Device token for push notifications (Web Push or Android FCM).
 *
 * Example:
 * const token: DeviceToken = {
 *   userId: "uuid-123",
 *   token: "push-token-here",
 *   platform: "web"
 * };
 */
export interface DeviceToken {
  id: string;
  userId: string;
  token: string;
  platform: 'web' | 'android';
  createdAt: string;
}

