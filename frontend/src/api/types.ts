export type Priority = 'high' | 'medium' | 'low';
export type ActionItemStatus = 'open' | 'in_progress' | 'complete';
export type ItemSource = 'manual' | 'insight';

export interface MeetingCreatePayload {
  transcript: string;
}

export interface Meeting {
  id: string;
  title: string;
  date: string;
  participants: string[];
  transcript: string;
  created_at: string;
  updated_at: string;
}

export interface GeneratedActionItem {
  owner: string;
  task: string;
  priority: Priority;
}

export interface Insight {
  id: string;
  meeting_id: string;
  generated_at: string;
  summary_short: string;
  summary_detailed: string;
  decisions: string[];
  blockers: string[];
  action_items: GeneratedActionItem[];
}

export interface ActionItem {
  id: string;
  meeting_id: string;
  owner: string;
  task: string;
  priority: Priority;
  status: ActionItemStatus;
  source: ItemSource;
  insight_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface MeetingListItem extends Meeting {
  action_item_count: number;
  open_action_item_count: number;
  completed_action_item_count: number;
  overdue_action_item_count: number;
  has_insights: boolean;
  summary_short: string | null;
}

export interface MeetingDetailResponse {
  meeting: Meeting;
  insight: Insight | null;
  action_items: ActionItem[];
}

export interface DashboardSummary {
  total_meetings: number;
  open_tasks: number;
  in_progress_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  recent_meetings: MeetingListItem[];
  overdue_action_items: ActionItem[];
}

export interface DeleteResponse {
  deleted: boolean;
}
