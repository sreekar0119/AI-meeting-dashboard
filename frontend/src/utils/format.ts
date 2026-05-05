import type { ActionItemStatus } from '../api/types';

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
});

const dateTimeFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
});

export function formatDate(value: string | null) {
  if (!value) {
    return 'No due date';
  }
  return dateFormatter.format(new Date(value));
}

export function formatDateTime(value: string) {
  return dateTimeFormatter.format(new Date(value));
}

export function getStatusLabel(status: ActionItemStatus) {
  switch (status) {
    case 'open':
      return 'Open';
    case 'in_progress':
      return 'In Progress';
    case 'complete':
      return 'Complete';
    default:
      return status;
  }
}

export function isOverdue(dueDate: string | null, status: ActionItemStatus) {
  if (!dueDate || status === 'complete') {
    return false;
  }
  const today = new Date();
  const due = new Date(dueDate);
  due.setHours(23, 59, 59, 999);
  return due.getTime() < today.getTime();
}
