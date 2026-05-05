import type { FormEvent } from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { apiClient } from '../api/client';
import { Card } from '../components/Card';
import { ErrorState } from '../components/ErrorState';

export function MeetingUploadPage() {
  const navigate = useNavigate();
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const payload = { transcript };
      const meeting = await apiClient.createMeeting(payload);
      await apiClient.generateInsights(meeting.id);
      navigate(`/meetings/${meeting.id}`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : 'Unable to save meeting.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr,0.85fr]">
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">New Meeting</p>
        <h2 className="mt-2 text-3xl font-bold text-ink">Upload a transcript and generate insights</h2>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Paste the transcript and the app will infer the meeting title, date, and participants before generating insights.
        </p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <label className="block text-sm font-semibold text-slate-600">
            Transcript
            <textarea
              className="mt-2 min-h-[280px] w-full rounded-[1.5rem] border border-brand-100 bg-white px-4 py-4 text-sm leading-6 text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
              onChange={(event) => setTranscript(event.target.value)}
              placeholder="Paste your transcript here"
              required
              value={transcript}
            />
            <span className={`mt-2 block text-xs ${transcript.length < 20 ? 'text-danger-600 font-semibold' : 'text-slate-400'}`}>
              {transcript.length} / 20 characters minimum required
            </span>
          </label>

          {error ? <ErrorState message={error} /> : null}

          <button
            className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={isSubmitting || transcript.length < 20}
            type="submit"
          >
            {isSubmitting ? 'Saving and generating...' : 'Save meeting and generate insights'}
          </button>
        </form>
      </Card>

      <div className="space-y-6">
        <Card className="bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 text-white">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">What gets created</p>
          <div className="mt-4 space-y-3 text-sm leading-6 text-brand-50">
            <p>A concise short summary for a manager skim.</p>
            <p>A detailed summary for follow-up context.</p>
            <p>Decisions, blockers, and action items tied to the meeting record.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
