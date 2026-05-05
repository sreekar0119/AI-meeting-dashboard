import { useMemo, useState } from 'react';

import { apiClient } from '../api/client';
import type { ActionItemStatus, MeetingListItem, Priority } from '../api/types';
import { ActionItemKanban } from '../components/ActionItemKanban';
import { Card } from '../components/Card';
import { ErrorState } from '../components/ErrorState';
import { LoadingState } from '../components/LoadingState';
import { useAsyncData } from '../hooks/useAsyncData';

export function ActionItemsPage() {
  const [statusFilter, setStatusFilter] = useState<ActionItemStatus | ''>('');
  const [ownerFilter, setOwnerFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<Priority | ''>('');
  const [meetingFilter, setMeetingFilter] = useState('');

  const meetingsState = useAsyncData(() => apiClient.listMeetings(), []);
  const actionItemsState = useAsyncData(
    () =>
      apiClient.listActionItems({
        meeting_id: meetingFilter || undefined,
        owner: ownerFilter || undefined,
        priority: priorityFilter || undefined,
        status: statusFilter || undefined,
      }),
    [meetingFilter, ownerFilter, priorityFilter, statusFilter],
  );

  const meetingsById = useMemo<Record<string, MeetingListItem>>(() => {
    return (meetingsState.data ?? []).reduce<Record<string, MeetingListItem>>((accumulator, meeting) => {
      accumulator[meeting.id] = meeting;
      return accumulator;
    }, {});
  }, [meetingsState.data]);

  const owners = useMemo(() => {
    const uniqueOwners = new Set((actionItemsState.data ?? []).map((item) => item.owner));
    return Array.from(uniqueOwners).sort((left, right) => left.localeCompare(right));
  }, [actionItemsState.data]);

  async function handleStatusChange(itemId: string, status: ActionItemStatus) {
    const updated = await apiClient.updateActionItemStatus(itemId, status);
    actionItemsState.setData((current) =>
      current?.map((item) => (item.id === updated.id ? updated : item)) ?? [],
    );
  }

  const hasError = meetingsState.error || actionItemsState.error;
  const isLoading = meetingsState.isLoading || actionItemsState.isLoading;

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 text-white">
        <div className="flex flex-col gap-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">Action Tracker</p>
            <h2 className="mt-2 text-3xl font-bold">Keep every follow-up visible.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-brand-50">
              Filter by owner, meeting, priority, or status, then move work forward directly from the dashboard.
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="text-sm font-semibold text-slate-600">
            Meeting
            <select
              className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
              value={meetingFilter}
              onChange={(event) => setMeetingFilter(event.target.value)}
            >
              <option value="">All meetings</option>
              {(meetingsState.data ?? []).map((meeting) => (
                <option key={meeting.id} value={meeting.id}>
                  {meeting.title}
                </option>
              ))}
            </select>
          </label>

          <label className="text-sm font-semibold text-slate-600">
            Owner
            <select
              className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
              value={ownerFilter}
              onChange={(event) => setOwnerFilter(event.target.value)}
            >
              <option value="">All owners</option>
              {owners.map((owner) => (
                <option key={owner} value={owner}>
                  {owner}
                </option>
              ))}
            </select>
          </label>

          <label className="text-sm font-semibold text-slate-600">
            Status
            <select
              className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as ActionItemStatus | '')}
            >
              <option value="">All statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="complete">Complete</option>
            </select>
          </label>

          <label className="text-sm font-semibold text-slate-600">
            Priority
            <select
              className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
              value={priorityFilter}
              onChange={(event) => setPriorityFilter(event.target.value as Priority | '')}
            >
              <option value="">All priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </label>
        </div>
      </Card>

      {isLoading ? <LoadingState label="Loading action items..." /> : null}
      {hasError ? (
        <ErrorState
          message={meetingsState.error ?? actionItemsState.error ?? 'Unknown error'}
          onRetry={() => {
            void meetingsState.refresh();
            void actionItemsState.refresh();
          }}
        />
      ) : null}

      {!isLoading && !hasError ? (
        <ActionItemKanban
          items={actionItemsState.data ?? []}
          meetingsById={meetingsById}
          onStatusChange={handleStatusChange}
        />
      ) : null}
    </div>
  );
}
