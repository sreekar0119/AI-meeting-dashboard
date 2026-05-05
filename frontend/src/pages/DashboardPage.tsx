import { Link } from 'react-router-dom';

import { apiClient } from '../api/client';
import { Card } from '../components/Card';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { KpiCard } from '../components/KpiCard';
import { LoadingState } from '../components/LoadingState';
import { MeetingCard } from '../components/MeetingCard';
import { useAsyncData } from '../hooks/useAsyncData';
import { formatDate } from '../utils/format';

export function DashboardPage() {
  const { data, error, isLoading, refresh } = useAsyncData(() => apiClient.getDashboardSummary(), []);

  if (isLoading) {
    return <LoadingState label="Loading manager view…" />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? 'Unable to load the dashboard.'} onRetry={() => void refresh()} />;
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Meetings"
          value={data.total_meetings}
          accentClassName="bg-brand-500"
          helperText="Stored locally in JSON with no database dependency."
        />
        <KpiCard
          label="Open Tasks"
          value={data.open_tasks}
          accentClassName="bg-danger-500"
          helperText="Work that still needs an owner push or first step."
        />
        <KpiCard
          label="In Progress"
          value={data.in_progress_tasks}
          accentClassName="bg-warning-500"
          helperText="Active follow-ups that are already moving."
        />
        <KpiCard
          label="Completed"
          value={data.completed_tasks}
          accentClassName="bg-success-500"
          helperText="Closed loop items completed by the team."
        />
      </section>

      <section className="grid gap-6">
        <Card>
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">Recent Meetings</p>
              <h2 className="mt-2 text-2xl font-bold text-ink">What changed most recently</h2>
            </div>
            <Link
              className="rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700"
              to="/meetings/new"
            >
              Add meeting
            </Link>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {data.recent_meetings.length > 0 ? (
              data.recent_meetings.map((meeting) => <MeetingCard key={meeting.id} meeting={meeting} />)
            ) : (
              <div className="lg:col-span-2">
                <EmptyState
                  title="No meetings yet"
                  description="Upload the first transcript to generate insights and populate the dashboard."
                />
              </div>
            )}
          </div>
        </Card>
      </section>
    </div>
  );
}
