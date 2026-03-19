'use client';

import { useEffect, useState } from 'react';

type Match = {
  matchId: number;
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  minute: string;
  status: string;
};

export default function LiveScores() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<string>('Connecting...');

  useEffect(() => {
    // Connect to the API Gateway using the current browser's hostname dynamically
    const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const eventSource = new EventSource(`http://${host}:8080/api/live-scores/stream`);

    eventSource.onopen = () => {
      setConnectionStatus('Connected (Live)');
    };

    eventSource.addEventListener('live-score-update', (event: any) => {
      const newMatch: Match = JSON.parse(event.data);
      setMatches((prevMatches) => {
        // Update existing match or add new one
        const exists = prevMatches.find(m => m.matchId === newMatch.matchId);
        if (exists) {
          return prevMatches.map(m => m.matchId === newMatch.matchId ? newMatch : m);
        }
        return [...prevMatches, newMatch];
      });
    });

    eventSource.onerror = () => {
      setConnectionStatus('Disconnected. Retrying...');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <div className="text-xs text-slate-400 mb-4 flex items-center justify-end">
        Status: <span className={connectionStatus.includes('Connected') ? 'text-emerald-400 ml-1' : 'text-amber-400 ml-1'}>{connectionStatus}</span>
      </div>

      {(() => {
        const liveMatches = matches.filter((m: Match) => m.status === 'LIVE');
        const finishedMatches = matches.filter((m: Match) => m.status === 'FINISHED');
        const displayMatches = liveMatches.length > 0 ? liveMatches : finishedMatches;

        if (displayMatches.length === 0) {
          return (
            <div className="bg-slate-800 rounded-xl p-8 text-center border border-slate-700">
              <p className="text-slate-400">Waiting for live matches to start...</p>
            </div>
          );
        }

        return (
          <div className="space-y-4">
            {liveMatches.length === 0 && (
              <div className="bg-slate-800/50 rounded-lg p-3 text-center border border-slate-700/50 mb-2">
                <p className="text-sm text-slate-400 font-medium">No live matches currently. Displaying recently finished matches.</p>
              </div>
            )}
            
            {displayMatches.map((match) => (
              <div key={match.matchId} className={`bg-slate-800 rounded-xl p-6 flex items-center justify-between border ${match.status === 'LIVE' ? 'border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.15)]' : 'border-slate-700'} shadow-sm transition-colors`}>
                
                <div className="flex-1 flex justify-end items-center space-x-4">
                  <span className="font-semibold text-lg">{match.homeTeam}</span>
                  <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center text-xs text-slate-400">HT</div>
                </div>

                <div className="flex-1 flex flex-col items-center justify-center px-6">
                  <div className="bg-slate-900 px-4 py-2 rounded-lg text-2xl font-bold tracking-widest tabular-nums text-emerald-400 border border-slate-700">
                    {match.homeScore} - {match.awayScore}
                  </div>
                  <div className={`text-sm font-medium mt-2 ${match.status === 'LIVE' ? 'text-red-400 animate-pulse' : 'text-slate-500'}`}>
                    {match.status === 'LIVE' ? match.minute : 'FT'}
                  </div>
                </div>

                <div className="flex-1 flex justify-start items-center space-x-4">
                  <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center text-xs text-slate-400">AT</div>
                  <span className="font-semibold text-lg">{match.awayTeam}</span>
                </div>

              </div>
            ))}
          </div>
        );
      })()}
    </div>
  );
}
