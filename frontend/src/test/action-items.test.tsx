import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { ActionItemsPage } from '../pages/ActionItemsPage';

const mockedApi = vi.hoisted(() => ({
  listMeetings: vi.fn(),
  listActionItems: vi.fn(),
  updateActionItemStatus: vi.fn(),
}));

vi.mock('../api/client', () => ({
  apiClient: {
    listMeetings: mockedApi.listMeetings,
    listActionItems: mockedApi.listActionItems,
    updateActionItemStatus: mockedApi.updateActionItemStatus,
  },
}));

describe('ActionItemsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApi.listMeetings.mockResolvedValue([
      {
        id: 'mtg_1',
        title: 'Product Launch',
        date: '2026-04-29',
        participants: ['Maya Chen'],
        transcript: 'Transcript',
        created_at: '2026-04-29T10:00:00Z',
        updated_at: '2026-04-29T10:00:00Z',
        action_item_count: 1,
        open_action_item_count: 1,
        completed_action_item_count: 0,
        overdue_action_item_count: 0,
        has_insights: true,
        summary_short: 'Summary',
      },
    ]);
    mockedApi.listActionItems.mockResolvedValue([
      {
        id: 'act_1',
        meeting_id: 'mtg_1',
        owner: 'Maya Chen',
        task: 'Finalize launch checklist',
        priority: 'high',
        status: 'open',
        source: 'manual',
        insight_id: null,
        created_at: '2026-04-29T10:00:00Z',
        updated_at: '2026-04-29T10:00:00Z',
      },
    ]);
    mockedApi.updateActionItemStatus.mockResolvedValue({
      id: 'act_1',
      meeting_id: 'mtg_1',
      owner: 'Maya Chen',
      task: 'Finalize launch checklist',
      priority: 'high',
      status: 'complete',
      source: 'manual',
      insight_id: null,
      created_at: '2026-04-29T10:00:00Z',
      updated_at: '2026-04-30T09:00:00Z',
    });
  });

  it('updates task status from the kanban board', async () => {
    render(
      <MemoryRouter>
        <ActionItemsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Finalize launch checklist')).toBeInTheDocument();
    const selector = screen.getByLabelText('Update status for Finalize launch checklist');
    await userEvent.selectOptions(selector, 'complete');

    await waitFor(() => {
      expect(mockedApi.updateActionItemStatus).toHaveBeenCalledWith('act_1', 'complete');
    });

    await waitFor(() => {
      expect(screen.getByLabelText('Update status for Finalize launch checklist')).toHaveValue('complete');
    });
  });
});
