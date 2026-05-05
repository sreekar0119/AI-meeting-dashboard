import { type FormEvent, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { apiClient } from '../api/client';
import { ActionItemTable } from '../components/ActionItemTable';
import { Card } from '../components/Card';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { LoadingState } from '../components/LoadingState';
import { useAsyncData } from '../hooks/useAsyncData';
import { formatDate, formatDateTime } from '../utils/format';

export function MeetingDetailPage() {
  const navigate = useNavigate();
  const { meetingId = '' } = useParams();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isCreatingAction, setIsCreatingAction] = useState(false);
  const [showActionForm, setShowActionForm] = useState(false);
  const [formData, setFormData] = useState({
    owner: '',
    task: '',
    priority: 'medium' as 'high' | 'medium' | 'low',
  });
  const { data, error, isLoading, refresh, setData } = useAsyncData(
    () => apiClient.getMeeting(meetingId),
    [meetingId],
  );

  const meetingsById = useMemo(() => {
    if (!data) {
      return {};
    }
    return {
      [data.meeting.id]: {
        ...data.meeting,
        action_item_count: data.action_items.length,
        open_action_item_count: data.action_items.filter((item) => item.status === 'open').length,
        completed_action_item_count: data.action_items.filter((item) => item.status === 'complete').length,
        overdue_action_item_count: 0,
        has_insights: Boolean(data.insight),
        summary_short: data.insight?.summary_short ?? null,
      },
    };
  }, [data]);

  async function handleGenerateInsights() {
    setActionError(null);
    setIsGenerating(true);
    try {
      await apiClient.generateInsights(meetingId);
      const refreshed = await apiClient.getMeeting(meetingId);
      setData(refreshed);
    } catch (caughtError) {
      setActionError(caughtError instanceof Error ? caughtError.message : 'Unable to generate insights.');
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleDeleteMeeting() {
    if (!window.confirm('Delete this meeting and all related insights and action items?')) {
      return;
    }

    setActionError(null);
    setIsDeleting(true);
    try {
      await apiClient.deleteMeeting(meetingId);
      navigate('/');
    } catch (caughtError) {
      setActionError(caughtError instanceof Error ? caughtError.message : 'Unable to delete meeting.');
      setIsDeleting(false);
    }
  }

  async function handleCreateActionItem(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setActionError(null);
    setIsCreatingAction(true);

    try {
      await apiClient.createActionItem({
        meeting_id: meetingId,
        owner: formData.owner,
        task: formData.task,
        priority: formData.priority,
      });
      const refreshed = await apiClient.getMeeting(meetingId);
      setData(refreshed);
      setShowActionForm(false);
      setFormData({
        owner: '',
        task: '',
        priority: 'medium',
      });
    } catch (caughtError) {
      setActionError(caughtError instanceof Error ? caughtError.message : 'Unable to create action item.');
    } finally {
      setIsCreatingAction(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading meeting details..." />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? 'Unable to load meeting details.'} onRetry={() => void refresh()} />;
  }

  const { meeting, insight, action_items: actionItems } = data;

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 text-white">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">
              Meeting Detail · {formatDate(meeting.date)}
            </p>
            <h2 className="mt-2 text-3xl font-bold">{meeting.title}</h2>
            <p className="mt-3 text-sm leading-6 text-brand-50">
              Participants: {meeting.participants.join(', ')}
            </p>
            <p className="mt-2 text-sm text-brand-100">
              Last updated {formatDateTime(meeting.updated_at)}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-brand-800 transition hover:bg-brand-50 disabled:cursor-not-allowed disabled:opacity-70"
              disabled={isGenerating || isDeleting}
              onClick={() => void handleGenerateInsights()}
              type="button"
            >
              {isGenerating ? 'Generating...' : insight ? 'Refresh insights' : 'Generate insights'}
            </button>
            <button
              className="rounded-full bg-danger-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-danger-700 disabled:cursor-not-allowed disabled:opacity-70"
              disabled={isDeleting || isGenerating}
              onClick={() => void handleDeleteMeeting()}
              type="button"
            >
              {isDeleting ? 'Deleting...' : 'Delete meeting'}
            </button>
            <Link
              className="rounded-full border border-brand-200 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-800/40"
              to="/action-items"
            >
              View all tasks
            </Link>
          </div>
        </div>
        {actionError ? <p className="mt-4 text-sm text-red-100">{actionError}</p> : null}
      </Card>

      <section className="grid gap-6 xl:grid-cols-[1.15fr,0.95fr]">
        <Card>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">Transcript</p>
          <h3 className="mt-2 text-2xl font-bold text-ink">Captured conversation</h3>
          <div className="mt-5 whitespace-pre-wrap rounded-[1.75rem] bg-slate-50/90 px-5 py-5 text-sm leading-7 text-slate-600">
            {meeting.transcript}
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">AI Insight</p>
                <h3 className="mt-2 text-2xl font-bold text-ink">Executive readout</h3>
              </div>
            </div>

            {insight ? (
              <div className="mt-5 space-y-5">
                <div className="rounded-[1.5rem] bg-brand-50 px-4 py-4">
                  <p className="text-sm font-semibold text-brand-900">{insight.summary_short}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{insight.summary_detailed}</p>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Decisions</p>
                    <ul className="mt-3 space-y-2">
                      {insight.decisions.map((decision) => (
                        <li key={decision} className="rounded-2xl bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
                          {decision}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Blockers</p>
                    {insight.blockers.length > 0 ? (
                      <ul className="mt-3 space-y-2">
                        {insight.blockers.map((blocker) => (
                          <li key={blocker} className="rounded-2xl bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
                            {blocker}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="mt-3 rounded-2xl bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
                        No blockers were identified.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-5">
                <EmptyState
                  title="Insights have not been generated yet"
                  description="Use the button above to create summaries, decisions, blockers, and action items."
                />
              </div>
            )}
          </Card>
        </div>
      </section>

      <Card>
        <div className="mb-5 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">Action Items</p>
            <h3 className="mt-2 text-2xl font-bold text-ink">Tracked follow-ups from this meeting</h3>
          </div>
          <button
            className="rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={isCreatingAction}
            onClick={() => setShowActionForm(!showActionForm)}
            type="button"
          >
            {showActionForm ? 'Cancel' : '+ Add Action Item'}
          </button>
        </div>
        <ActionItemTable items={actionItems} meetingsById={meetingsById} showMeeting={false} />
      </Card>

      {showActionForm && (
        <Card className="border-2 border-brand-500">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">New Action Item</p>
          <h3 className="mt-2 text-2xl font-bold text-ink">Create a manual action item</h3>

          <form className="mt-6 space-y-5" onSubmit={handleCreateActionItem}>
            <div className="grid gap-5 md:grid-cols-2">
              <label className="text-sm font-semibold text-slate-600">
                Owner
                <input
                  className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
                  onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
                  placeholder="Ex: John Doe"
                  required
                  value={formData.owner}
                />
              </label>

              <label className="text-sm font-semibold text-slate-600">
                Priority
                <select
                  className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as 'high' | 'medium' | 'low' })}
                  required
                  value={formData.priority}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </label>
            </div>

            <label className="text-sm font-semibold text-slate-600">
              Task Description
              <textarea
                className="mt-2 w-full rounded-2xl border border-brand-100 bg-white px-4 py-3 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
                onChange={(e) => setFormData({ ...formData, task: e.target.value })}
                placeholder="Ex: Prepare budget proposal for next quarter"
                required
                rows={3}
                value={formData.task}
              />
            </label>

            <div className="flex gap-3 pt-2">
              <button
                className="flex-1 rounded-full bg-brand-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-70"
                disabled={isCreatingAction}
                type="submit"
              >
                {isCreatingAction ? 'Creating...' : 'Create Action Item'}
              </button>
              <button
                className="flex-1 rounded-full border border-brand-200 px-4 py-3 text-sm font-semibold text-brand-500 transition hover:bg-brand-50"
                disabled={isCreatingAction}
                onClick={() => setShowActionForm(false)}
                type="button"
              >
                Cancel
              </button>
            </div>
          </form>
        </Card>
      )}
    </div>
  );
}
