/**
 * Client-side mirror of identity's domain types (see docs/ARCHITECTURE.md:
 * "domain/ - Tipos y modelos de dominio del cliente, en espejo con los
 * bounded contexts del backend"). No business logic here - the backend
 * is the single source of truth; the client only shapes the data it
 * receives.
 */

export interface User {
  id: string;
  email: string;
}

export interface AuthSession {
  accessToken: string;
  user: User;
}
