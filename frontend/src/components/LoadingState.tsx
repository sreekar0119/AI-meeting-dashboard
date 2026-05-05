export function LoadingState({ label = 'Loading dashboard…' }: { label?: string }) {
  return (
    <div className="rounded-[2rem] border border-white/70 bg-white/75 px-5 py-12 text-center shadow-panel">
      <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-500" />
      <p className="mt-4 text-sm font-medium text-slate-500">{label}</p>
    </div>
  );
}
