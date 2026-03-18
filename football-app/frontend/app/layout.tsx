import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Football Live App',
  description: 'Real-time football scores and upcoming fixtures',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-900 text-slate-50 font-sans">
        <header className="bg-emerald-600 shadow-md">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold tracking-tight text-white flex items-center">
              <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              LiveFootball
            </h1>
          </div>
        </header>
        <main>{children}</main>
        <footer className="bg-slate-800 text-center py-6 mt-12 text-slate-400">
          <p>&copy; {new Date().getFullYear()} LiveFootball App. Next.js + Spring Boot.</p>
        </footer>
      </body>
    </html>
  );
}
