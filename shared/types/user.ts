// User related types

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer'
}

export interface User {
  uid: string;
  email: string;
  display_name?: string;
  role: UserRole;
  created_at: Date;
  updated_at: Date;
  last_login?: Date;
  is_active: boolean;
}

export interface UserProfile {
  uid: string;
  email: string;
  display_name?: string;
  role: UserRole;
  preferences: UserPreferences;
  statistics: UserStatistics;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  notifications_enabled: boolean;
  default_priority: string;
  auto_save_enabled: boolean;
}

export interface UserStatistics {
  total_cases_generated: number;
  cases_this_month: number;
  avg_generation_time: number;
  favorite_agent: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: AuthToken;
} 