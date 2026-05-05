import { NavLink, Outlet } from 'react-router-dom';

const navigationItems = [
  { label: 'Dashboard', path: '/' },
  { label: 'New Meeting', path: '/meetings/new' },
  { label: 'Action Items', path: '/action-items' },
];

function navClassName(isActive: boolean) {
  return [
    'rounded-full px-4 py-2 text-sm font-semibold transition',
    isActive
      ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25'
      : 'bg-white/70 text-slate-600 hover:bg-white hover:text-ink',
  ].join(' ');
}

export function AppShell() {
  return (
    <div className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 rounded-[2rem] border border-white/70 bg-white/70 px-5 py-5 shadow-panel backdrop-blur sm:px-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-brand-600">
                AI Meeting Insights Dashboard
              </p>
              
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
                Generate structured insights, and keep every follow-up visible.
              </p>
            </div>
    
          </div>

          <nav className="mt-5 flex flex-wrap gap-3">
            {navigationItems.map((item) => (
              <NavLink key={item.path} className={({ isActive }) => navClassName(isActive)} to={item.path} end={item.path === '/'}>
                {item.label}
              </NavLink>
            ))}
          </nav>
        </header>

        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
