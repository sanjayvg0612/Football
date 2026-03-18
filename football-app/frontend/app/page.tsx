'use client';

import LiveScores from '@/components/LiveScores';
import UpcomingFixtures from '@/components/UpcomingFixtures';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Column: Live Scores */}
        <div className="lg:col-span-2 space-y-8">
          <section>
            <div className="flex items-center justify-between mb-4 border-b border-slate-700 pb-2">
              <h2 className="text-2xl font-semibold flex items-center">
                <span className="relative flex h-3 w-3 mr-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
                Live Matches
              </h2>
            </div>
            <LiveScores />
          </section>
        </div>

        {/* Sidebar: Upcoming Fixtures */}
        <div className="lg:col-span-1 space-y-8">
          <section className="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-b border-slate-700 pb-2 flex items-center text-emerald-400">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              Upcoming Fixtures
            </h2>
            <UpcomingFixtures />
          </section>
        </div>

      </div>
    </div>
  );
}
