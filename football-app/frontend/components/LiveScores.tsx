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
    // Connect to the API Gateway routing to the Live Score Service
    const eventSource = new EventSource('http://localhost:8080/api/live-scores/stream');

    eventSource.onopen = () => {
      setConnectionStatus('Connected (Live)');
    };

    eventSource.addEventListener('live-score-update', (event) => {
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

      {matches.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-8 text-center border border-slate-700">
          <p className="text-slate-400">Waiting for live matches to start...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <div key={match.matchId} className="bg-slate-800 rounded-xl p-6 flex items-center justify-between border border-slate-700 shadow-sm hover:border-emerald-500 transition-colors">
              
              <div className="flex-1 flex justify-end items-center space-x-4">
                <span className="font-semibold text-lg">{match.homeTeam}</span>
                {/* Mock Team Logo */}
                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center text-xs text-slate-400">HT</div>
              </div>

              <div className="flex-1 flex flex-col items-center justify-center px-6">
                <div className="bg-slate-900 px-4 py-2 rounded-lg text-2xl font-bold tracking-widest tabular-nums text-emerald-400 border border-slate-700">
                  {match.homeScore} - {match.awayScore}
                </div>
                <div className="text-sm text-red-400 font-medium mt-2 animate-pulse">
                  {match.minute}
                </div>
              </div>

              <div className="flex-1 flex justify-start items-center space-x-4">
                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center text-xs text-slate-400">AT</div>
                <span className="font-semibold text-lg">{match.awayTeam}</span>
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}
