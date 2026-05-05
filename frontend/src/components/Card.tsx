import type { PropsWithChildren } from 'react';

interface CardProps extends PropsWithChildren {
  className?: string;
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <section className={`rounded-[2rem] border border-white/70 bg-white/85 p-5 shadow-panel backdrop-blur ${className}`}>
      {children}
    </section>
  );
}
