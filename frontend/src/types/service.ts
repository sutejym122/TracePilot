export type Environment = "dev" | "uat" | "prod";
export type ServiceStatus = "healthy" | "degraded" | "down" | "unknown";

export interface Service {
  id: string;
  user_id: string;
  name: string;
  owner: string | null;
  environment: Environment;
  status: ServiceStatus;
  repo_url: string | null;
  health_url: string | null;
  last_deployed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ServiceCreate {
  name: string;
  environment: Environment;
  owner?: string | null;
  repo_url?: string | null;
  health_url?: string | null;
  last_deployed_at?: string | null;
}

export type ServiceUpdate = Partial<ServiceCreate>;
