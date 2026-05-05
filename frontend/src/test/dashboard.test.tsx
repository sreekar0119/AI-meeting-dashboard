import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { DashboardPage } from '../pages/DashboardPage';

const mockedApi = vi.hoisted(() => ({
  getDashboardSummary: vi.fn(),
}));

vi.mock('../api/client', () => ({
  apiClient: {
    getDashboardSummary: mockedApi.getDashboardSummary,
  },
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApi.getDashboardSummary.mockResolvedValue({
      total_meetings: 5,
      open_tasks: 6,
      in_progress_tasks: 4,
      completed_tasks: 5,
      overdue_tasks: 2,
      recent_meetings: [
        {
          id: 'mtg_1',
          title: 'Q2 Sales Forecast Sync',
          date: '2026-04-24',
          participants: ['Alice Johnson', 'Ben Carter'],
          transcript: 'Transcript',
          created_at: '2026-04-24T10:00:00Z',
          updated_at: '2026-04-24T10:00:00Z',
          action_item_count: 3,
          open_action_item_count: 1,
          completed_action_item_count: 1,
          overdue_action_item_count: 1,
          has_insights: true,
          summary_short: 'Forecast aligned with one blocker and three follow-ups.',
        },
      ],
      overdue_action_items: [
        {
          id: 'act_1',
          meeting_id: 'mtg_1',
          owner: 'Ben Carter',
          task: 'Close CRM export validation gap',
          priority: 'high',
          status: 'open',
          source: 'insight',
          insight_id: 'ins_1',
          created_at: '2026-04-24T10:00:00Z',
          updated_at: '2026-04-24T10:00:00Z',
        },
      ],
    });
  });

  it('renders KPI cards and recent meetings', async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Q2 Sales Forecast Sync')).toBeInTheDocument();
    expect(screen.getByText('Meetings')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Overdue follow-ups')).toBeInTheDocument();
    expect(screen.getByText('Close CRM export validation gap')).toBeInTheDocument();
  });
});
