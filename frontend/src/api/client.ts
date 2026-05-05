import type {
  ActionItem,
  ActionItemStatus,
  DashboardSummary,
  DeleteResponse,
  Insight,
  Meeting,
  MeetingCreatePayload,
  MeetingDetailResponse,
  MeetingListItem,
  Priority,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

type QueryValue = string | boolean | undefined | null;

function buildQuery(params: Record<string, QueryValue>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value));
    }
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : '';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const errorPayload = (await response.json()) as {
        detail?: string | Array<{ msg?: string; loc?: string[] }>;
      };
      if (typeof errorPayload.detail === 'string') {
        message = errorPayload.detail;
      } else if (Array.isArray(errorPayload.detail)) {
        // Handle Pydantic validation errors
        const errors = errorPayload.detail
          .map((err) => {
            const field = err.loc?.[1] || err.loc?.[0] || 'unknown field';
            return `${field}: ${err.msg || 'validation error'}`;
          })
          .join('; ');
        message = errors || 'Validation error';
      }
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const apiClient = {
  getDashboardSummary(): Promise<DashboardSummary> {
    return request<DashboardSummary>('/dashboard');
  },
  listMeetings(filters?: {
    date_from?: string;
    date_to?: string;
    participant?: string;
    owner?: string;
    status?: ActionItemStatus;
  }): Promise<MeetingListItem[]> {
    return request<MeetingListItem[]>(`/meetings${buildQuery(filters ?? {})}`);
  },
  createMeeting(payload: MeetingCreatePayload): Promise<Meeting> {
    return request<Meeting>('/meetings', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  getMeeting(meetingId: string): Promise<MeetingDetailResponse> {
    return request<MeetingDetailResponse>(`/meetings/${meetingId}`);
  },
  deleteMeeting(meetingId: string): Promise<DeleteResponse> {
    return request<DeleteResponse>(`/meetings/${meetingId}`, {
      method: 'DELETE',
    });
  },
  generateInsights(meetingId: string): Promise<Insight> {
    return request<Insight>(`/meetings/${meetingId}/insights`, {
      method: 'POST',
    });
  },
  listActionItems(filters?: {
    meeting_id?: string;
    owner?: string;
    status?: ActionItemStatus;
    priority?: Priority;
    overdue?: boolean;
  }): Promise<ActionItem[]> {
    return request<ActionItem[]>(`/action-items${buildQuery(filters ?? {})}`);
  },
  updateActionItemStatus(itemId: string, status: ActionItemStatus): Promise<ActionItem> {
    return request<ActionItem>(`/action-items/${itemId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },
  createActionItem(payload: {
    meeting_id: string;
    owner: string;
    task: string;
    priority: Priority;
  }): Promise<ActionItem> {
    return request<ActionItem>('/action-items', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
