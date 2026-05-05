import { Card } from './Card';

interface KpiCardProps {
  label: string;
  value: number;
  accentClassName: string;
  helperText: string;
}

export function KpiCard({ label, value, accentClassName, helperText }: KpiCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className={`absolute inset-x-0 top-0 h-1.5 ${accentClassName}`} />
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{label}</p>
      <p className="mt-4 text-4xl font-bold text-ink">{value}</p>
      <p className="mt-3 text-sm text-slate-500">{helperText}</p>
    </Card>
  );
}
