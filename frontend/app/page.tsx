'use client';

import { useState } from 'react';

interface SpeakerMatch {
  name: string;
  title: string;
  organization: string;
  bio: string;
  score: number;
  reasoning: string;
}

interface MatchResponse {
  matches: SpeakerMatch[];
  total_speakers: number;
  matches_found: number;
}

export default function Home() {
  const [userBio, setUserBio] = useState('');
  const [threshold, setThreshold] = useState(7.0);
  const [allMatches, setAllMatches] = useState<SpeakerMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [totalSpeakers, setTotalSpeakers] = useState(0);
  const [showLowScores, setShowLowScores] = useState(false);
  const [expandedSpeaker, setExpandedSpeaker] = useState<number | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (userBio.trim().length < 10) {
      setError('Please enter at least 10 characters');
      return;
    }

    setLoading(true);
    setError('');
    setAllMatches([]);
    setShowLowScores(false);

    try {
      const response = await fetch('http://localhost:8000/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_bio: userBio,
          threshold: 0,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }

      const data: MatchResponse = await response.json();
      setAllMatches(data.matches);
      setTotalSpeakers(data.total_speakers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    'I sell Counter-Unmanned Aircraft Systems for an Army Air Base',
    'I sell kamikaze drones that destroy tanks, and I am a small business',
    'I\'m looking for partnerships in special operations technology',
  ];

  const topMatches = allMatches.filter(m => m.score >= threshold);
  const lowMatches = allMatches.filter(m => m.score < threshold);

  const getScoreBadge = (score: number) => {
    if (score >= 9) return 'bg-emerald-500';
    if (score >= 7) return 'bg-blue-500';
    if (score >= 5) return 'bg-amber-500';
    return 'bg-gray-400';
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-semibold text-gray-900">
            SOFWeek Speaker Intelligence
          </h1>
          <p className="text-gray-600 mt-1">
            AI-powered speaker matching for strategic networking
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Input Section */}
        <div className="mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Describe your business and goals
              </label>
              <textarea
                value={userBio}
                onChange={(e) => setUserBio(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent text-gray-900 placeholder-gray-400 resize-none"
                rows={3}
                placeholder="e.g., I sell Counter-Unmanned Aircraft Systems for an Army Air Base"
                disabled={loading}
              />
            </div>

            <div className="flex items-center gap-6">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Match threshold: {threshold.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.5"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-black"
                  disabled={loading}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0</span>
                  <span>5</span>
                  <span>10</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {loading ? 'Analyzing...' : 'Find Matches'}
              </button>
            </div>

            {/* Example Prompts */}
            <div className="flex flex-wrap gap-2 pt-2">
              <span className="text-xs text-gray-500 self-center">Try:</span>
              {examplePrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setUserBio(prompt)}
                  className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                  disabled={loading}
                >
                  {prompt.length > 50 ? prompt.substring(0, 50) + '...' : prompt}
                </button>
              ))}
            </div>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {loading && (
            <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-black"></div>
                <p className="text-gray-700 text-sm">
                  Analyzing {totalSpeakers || 36} speakers in parallel...
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        {topMatches.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {topMatches.length} matches found (&gt;= {threshold})
              </h2>
              <span className="text-sm text-gray-500">
                {allMatches.length} total analyzed
              </span>
            </div>

            <div className="space-y-3">
              {topMatches.map((match, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-lg bg-white hover:border-gray-300 transition-colors"
                >
                  <div 
                    className="p-5 cursor-pointer hover:bg-gray-50"
                    onClick={() => {
                      console.log('Clicked speaker', idx, 'Current expanded:', expandedSpeaker);
                      setExpandedSpeaker(expandedSpeaker === idx ? null : idx);
                    }}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-sm font-medium text-gray-500">
                            #{idx + 1}
                          </span>
                          <h3 className="text-lg font-semibold text-gray-900 truncate">
                            {match.name}
                          </h3>
                          <div className={`px-2 py-0.5 ${getScoreBadge(match.score)} text-white text-xs font-medium rounded`}>
                            {match.score.toFixed(1)}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-1">{match.title}</p>
                        <p className="text-sm text-gray-500 mb-3">{match.organization}</p>
                        <div className="pt-3 border-t border-gray-100">
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {match.reasoning}
                          </p>
                        </div>
                      </div>
                      <div className="text-gray-400 text-sm shrink-0">
                        {expandedSpeaker === idx ? '▼' : '▶'}
                      </div>
                    </div>
                  </div>
                  
                  {expandedSpeaker === idx && (
                    <div className="px-5 pb-5 pt-0 border-t border-gray-100">
                      <div className="mt-4">
                        <h4 className="text-sm font-semibold text-gray-900 mb-2">Full Bio</h4>
                        {match.bio ? (
                          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                            {match.bio}
                          </p>
                        ) : (
                          <p className="text-sm text-gray-500 italic">No bio available</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Lower Matches */}
            {lowMatches.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setShowLowScores(!showLowScores)}
                  className="text-sm text-gray-600 hover:text-gray-900 font-medium"
                >
                  {showLowScores ? 'Hide' : 'Show'} {lowMatches.length} lower priority matches (below {threshold})
                </button>

                {showLowScores && (
                  <div className="mt-4 space-y-2">
                    {lowMatches.map((match, idx) => {
                      const lowIdx = topMatches.length + idx;
                      return (
                        <div
                          key={idx}
                          className="border border-gray-200 rounded-lg bg-gray-50"
                        >
                          <div 
                            className="p-4 cursor-pointer"
                            onClick={() => setExpandedSpeaker(expandedSpeaker === lowIdx ? null : lowIdx)}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`px-2 py-0.5 ${getScoreBadge(match.score)} text-white text-xs font-medium rounded shrink-0`}>
                                {match.score.toFixed(1)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="text-sm font-semibold text-gray-900 mb-1">
                                  {match.name}
                                </h3>
                                <p className="text-xs text-gray-600 mb-1">{match.title}</p>
                                <p className="text-xs text-gray-500 mb-2">{match.organization}</p>
                                <p className="text-xs text-gray-600 leading-relaxed">
                                  {match.reasoning}
                                </p>
                              </div>
                              <div className="text-gray-400 text-xs shrink-0">
                                {expandedSpeaker === lowIdx ? '▼' : '▶'}
                              </div>
                            </div>
                          </div>
                          
                          {expandedSpeaker === lowIdx && (
                            <div className="px-4 pb-4 pt-0 border-t border-gray-200">
                              <div className="mt-3">
                                <h4 className="text-xs font-semibold text-gray-900 mb-2">Full Bio</h4>
                                {match.bio ? (
                                  <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-line">
                                    {match.bio}
                                  </p>
                                ) : (
                                  <p className="text-xs text-gray-500 italic">No bio available</p>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Info Footer */}
        {!loading && allMatches.length === 0 && (
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">How it works</h3>
                <ol className="text-gray-600 space-y-1">
                  <li>1. Enter your business context</li>
                  <li>2. AI scores each speaker (0-10)</li>
                  <li>3. Review ranked matches</li>
                  <li>4. Plan your conversations</li>
                </ol>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Score guide</h3>
                <ul className="text-gray-600 space-y-1">
                  <li>9-10: Critical contact</li>
                  <li>7-8: High priority</li>
                  <li>5-6: Moderate value</li>
                  <li>0-4: Low priority</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">About</h3>
                <p className="text-gray-600">
                  Powered by GPT-4.1, analyzing {totalSpeakers || 36} SOFWeek 2025 speakers in parallel.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
