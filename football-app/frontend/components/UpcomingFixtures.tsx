'use client';

import { useEffect, useState } from 'react';

type Fixture = {
  id: number;
  homeTeam: string;
  awayTeam: string;
  matchDate: string;
  league: string;
  status: string;
};

export default function UpcomingFixtures() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFixtures = async () => {
      try {
        // Mock data fallback in case backend is not running
        const mockData: Fixture[] = [
          { id: 1, homeTeam: 'Liverpool', awayTeam: 'Man City', matchDate: '2026-03-22T16:00:00', league: 'Premier League', status: 'SCHEDULED' },
          { id: 2, homeTeam: 'Real Madrid', awayTeam: 'Barcelona', matchDate: '2026-03-24T20:00:00', league: 'La Liga', status: 'SCHEDULED' },
          { id: 3, homeTeam: 'Bayern Munich', awayTeam: 'Dortmund', matchDate: '2026-03-25T18:30:00', league: 'Bundesliga', status: 'SCHEDULED' }
        ];

        try {
          // Attempting to fetch from API Gateway (Fixture Service)
          const res = await fetch('http://localhost:8080/api/fixtures/upcoming');
          if (res.ok) {
            const data = await res.json();
            if (data && data.length > 0) {
              setFixtures(data);
              setLoading(false);
              return;
            }
          }
        } catch (e) {
          console.log("Backend not reachable, using mock data for UI strictly.");
        }
        
        // Fallback to mock data if fetch fails or returns empty
        setFixtures(mockData);
        setLoading(false);

      } catch (err) {
        setError('Failed to load fixtures');
        setLoading(false);
      }
    };

    fetchFixtures();
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-4">Loading fixtures...</div>;
  if (error) return <div className="text-red-400 text-sm py-4">{error}</div>;

  return (
    <div className="space-y-4">
      {fixtures.map((fixture) => {
        const date = new Date(fixture.matchDate);
        return (
          <div key={fixture.id} className="bg-slate-900 rounded-lg p-4 border border-slate-700 hover:border-slate-500 transition-colors">
            <div className="text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">
              {fixture.league}
            </div>
            
            <div className="flex justify-between items-center text-sm font-medium">
              <div className="flex-1 text-right">{fixture.homeTeam}</div>
              <div className="px-3 text-slate-500">vs</div>
              <div className="flex-1 text-left">{fixture.awayTeam}</div>
            </div>
            
            <div className="mt-3 text-center text-xs text-emerald-400 bg-slate-800 py-1 rounded">
              {date.toLocaleDateString()} - {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
