import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { MeetingDetailPage } from '../pages/MeetingDetailPage';

const mockedApi = vi.hoisted(() => ({
  getMeeting: vi.fn(),
  deleteMeeting: vi.fn(),
  generateInsights: vi.fn(),
}));

vi.mock('../api/client', () => ({
  apiClient: {
    getMeeting: mockedApi.getMeeting,
    deleteMeeting: mockedApi.deleteMeeting,
    generateInsights: mockedApi.generateInsights,
  },
}));

describe('MeetingDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApi.getMeeting.mockResolvedValue({
      meeting: {
        id: 'mtg_1',
        title: 'Renewal Planning Sync',
        date: '2026-04-30',
        participants: ['Ava Moore', 'Chris Lane'],
        transcript: 'Ava Moore: We agreed to move forward.',
        created_at: '2026-04-30T10:00:00Z',
        updated_at: '2026-04-30T10:00:00Z',
      },
      insight: null,
      action_items: [],
    });
    mockedApi.deleteMeeting.mockResolvedValue({ deleted: true });
    mockedApi.generateInsights.mockResolvedValue({
      id: 'ins_1',
      meeting_id: 'mtg_1',
      generated_at: '2026-04-30T10:05:00Z',
      summary_short: 'Short summary',
      summary_detailed: 'Detailed summary',
      decisions: [],
      blockers: [],
      action_items: [],
    });
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  });

  it('deletes a meeting from the detail page', async () => {
    render(
      <MemoryRouter initialEntries={['/meetings/mtg_1']}>
        <Routes>
          <Route path="/" element={<div>Dashboard</div>} />
          <Route path="/meetings/:meetingId" element={<MeetingDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Renewal Planning Sync')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Delete meeting' }));

    await waitFor(() => {
      expect(mockedApi.deleteMeeting).toHaveBeenCalledWith('mtg_1');
    });

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
  });
});
