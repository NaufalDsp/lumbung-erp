/**
 * Robust API Client with Cold-Start Detection, Token Management, and Demo Persona Switcher.
 */

export interface UserSession {
  id: number;
  email: string;
  name: string;
  role: "admin" | "sales" | "warehouse" | "finance";
  is_active: boolean;
  avatar_url?: string;
}

export interface ApiResponse<T = any> {
  data: T;
  error?: string;
  statusCode: number;
}

const API_BASE = (import.meta as any).env?.VITE_API_BASE || "/api/v1";

class ApiClient {
  private accessToken: string | null = null;
  private currentUser: UserSession | null = null;
  private isColdStart: boolean = false;
  private coldStartListeners: Array<(isCold: boolean) => void> = [];

  constructor() {
    this.accessToken = localStorage.getItem("lumbung_token");
    const storedUser = localStorage.getItem("lumbung_user");
    if (storedUser) {
      try {
        this.currentUser = JSON.parse(storedUser);
      } catch {
        this.currentUser = null;
      }
    }
  }

  public subscribeColdStart(callback: (isCold: boolean) => void): () => void {
    this.coldStartListeners.push(callback);
    callback(this.isColdStart);
    return () => {
      this.coldStartListeners = this.coldStartListeners.filter(
        (cb) => cb !== callback,
      );
    };
  }

  private setColdStart(val: boolean) {
    if (this.isColdStart !== val) {
      this.isColdStart = val;
      this.coldStartListeners.forEach((cb) => cb(val));
    }
  }

  public getCurrentUser(): UserSession | null {
    return this.currentUser;
  }

  public getToken(): string | null {
    return this.accessToken;
  }

  public setSession(token: string, user: UserSession) {
    this.accessToken = token;
    this.currentUser = user;
    localStorage.setItem("lumbung_token", token);
    localStorage.setItem("lumbung_user", JSON.stringify(user));
  }

  public clearSession() {
    this.accessToken = null;
    this.currentUser = null;
    localStorage.removeItem("lumbung_token");
    localStorage.removeItem("lumbung_user");
  }

  /**
   * Pings /health endpoint to detect cold-start or database connectivity.
   */
  public async checkHealth(): Promise<{ status: string; database: boolean }> {
    try {
      const resp = await fetch(`${API_BASE}/health`, { method: "GET" });
      if (resp.ok) {
        this.setColdStart(false);
        const data = await resp.json();
        return { status: "healthy", database: data.database ?? true };
      }
      this.setColdStart(true);
      return { status: "degraded", database: false };
    } catch {
      // If request took longer than 3 seconds or failed to connect, flag as cold start
      this.setColdStart(true);
      return { status: "cold_start", database: false };
    }
  }

  /**
   * Enterprise User Login with standard email & password.
   */
  public async login(email: string, password: string): Promise<UserSession> {
    const resp = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!resp.ok) {
      let msg = "Kombinasi email dan kata sandi tidak cocok";
      try {
        const err = await resp.json();
        msg =
          err.detail?.error?.message ||
          err.detail?.message ||
          err.detail ||
          msg;
      } catch {
        // use default message
      }
      throw new Error(msg);
    }

    const data = await resp.json();
    this.setSession(data.access_token, data.user);
    this.setColdStart(false);
    return data.user;
  }

  /**
   * Terminates active session.
   */
  public async logout(): Promise<void> {
    try {
      await this.post("/auth/logout");
    } catch {
      // ignore network errors on logout
    } finally {
      this.clearSession();
    }
  }

  /**
   * Internal session switcher for role-based testing.
   */
  public async switchRole(
    role: "admin" | "sales" | "warehouse" | "finance",
  ): Promise<UserSession> {
    const resp = await fetch(`${API_BASE}/auth/demo-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });

    if (!resp.ok) {
      throw new Error("Gagal beralih akun");
    }

    const data = await resp.json();
    this.setSession(data.access_token, data.user);
    this.setColdStart(false);
    return data.user;
  }

  /**
   * Core request wrapper with authorization and cold-start fallback.
   */
  public async request<T = any>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.accessToken) {
      headers["Authorization"] = `Bearer ${this.accessToken}`;
    }

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (res.status === 401) {
        this.clearSession();
        throw new Error("Sesi login berakhir. Silakan login kembali.");
      }

      if (!res.ok) {
        let errMessage = `Error ${res.status}`;
        try {
          const errData = await res.json();
          errMessage = errData.detail?.message || errData.detail || errMessage;
        } catch {
          // ignore parsing error
        }
        throw new Error(errMessage);
      }

      this.setColdStart(false);
      return await res.json();
    } catch (err: any) {
      if (err.name === "TypeError" && err.message?.includes("fetch")) {
        this.setColdStart(true);
      }
      throw err;
    }
  }

  public get<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  public post<T = any>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public put<T = any>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

export const api = new ApiClient();
