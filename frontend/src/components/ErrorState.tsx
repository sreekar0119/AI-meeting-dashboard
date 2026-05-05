interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-[2rem] border border-danger-100 bg-white/80 px-5 py-8 text-center shadow-panel">
      <p className="text-lg font-semibold text-danger-700">Something needs attention</p>
      <p className="mt-2 text-sm text-slate-600">{message}</p>
      {onRetry ? (
        <button
          className="mt-4 rounded-full bg-danger-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-danger-700"
          onClick={onRetry}
          type="button"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}
