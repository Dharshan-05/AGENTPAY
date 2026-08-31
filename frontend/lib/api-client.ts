import { ApiResponseEnvelope } from './types/api';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export class ApiClientError extends Error {
  public status: number;
  public code?: string;
  public requestId?: string;
  public details?: any;

  constructor(message: string, status: number, code?: string, requestId?: string, details?: any) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.details = details;
  }
}

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
  skipAuth?: boolean;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = (baseUrl || process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '');
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    try {
      return localStorage.getItem('agentpay_token');
    } catch {
      return null;
    }
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number | boolean | undefined | null>): string {
    let cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    // Auto-prefix /api/v1 if not already present
    if (!cleanEndpoint.startsWith('/api/v1') && !cleanEndpoint.startsWith('/docs') && !cleanEndpoint.startsWith('/openapi.json')) {
      cleanEndpoint = `/api/v1${cleanEndpoint}`;
    }

    const fullUrl = new URL(`${this.baseUrl}${cleanEndpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          fullUrl.searchParams.append(key, String(value));
        }
      });
    }

    return fullUrl.toString();
  }

  public async request<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, skipAuth, headers: customHeaders, ...fetchOptions } = options;
    const url = this.buildUrl(endpoint, params);

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(customHeaders as Record<string, string>),
    };

    if (!skipAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      });

      const requestId = response.headers.get('X-Request-ID') || undefined;

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      let payload: ApiResponseEnvelope<T> | any;
      const contentType = response.headers.get('content-type') || '';
      
      if (contentType.includes('application/json')) {
        payload = await response.json();
      } else {
        const text = await response.text();
        if (!response.ok) {
          throw new ApiClientError(text || `HTTP ${response.status}`, response.status, undefined, requestId);
        }
        return text as unknown as T;
      }

      // Check if backend returned standard envelope
      if (payload && typeof payload === 'object' && 'success' in payload) {
        const reqId = payload.meta?.request_id || requestId;
        if (!payload.success || response.status >= 400) {
          const errCode = payload.error?.code || `HTTP_${response.status}`;
          const errMessage = payload.error?.message || 'An unexpected error occurred.';
          throw new ApiClientError(errMessage, response.status, errCode, reqId, payload.error?.details);
        }
        return payload.data as T;
      }

      // Non-wrapped direct JSON response
      if (!response.ok) {
        const detailMsg = payload?.detail || payload?.message || `Request failed with status ${response.status}`;
        throw new ApiClientError(detailMsg, response.status, undefined, requestId);
      }

      return payload as T;
    } catch (error) {
      if (error instanceof ApiClientError) {
        throw error;
      }
      throw new ApiClientError((error as Error).message || 'Network error', 0);
    }
  }

  public get<T = any>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  public put<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  public patch<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  public delete<T = any>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
