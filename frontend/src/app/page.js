"use client";

import { useState } from "react";
import EmailForm from "@/components/EmailForm";
import EmailResults from "@/components/EmailResults";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async ({ firstName, lastName, company }) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    try {
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          company: company,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate emails");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-zinc-900 via-zinc-950 to-zinc-900" />
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
      
      <div className="relative z-10 container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Email <span className="text-emerald-400">Finder</span>
          </h1>
          <p className="text-zinc-400 text-lg max-w-md mx-auto">
            Find anyone&apos;s email address by entering their name and company. 
            We&apos;ll generate the most common email patterns.
          </p>
        </div>

        {/* Main content */}
        <div className="flex flex-col lg:flex-row items-start justify-center gap-8 max-w-6xl mx-auto">
          {/* Form card */}
          <div className="w-full lg:w-1/3 bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 
                          rounded-2xl p-8 shadow-2xl">
            <EmailForm onGenerate={handleGenerate} isLoading={isLoading} />
            
            {error && (
              <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Results card */}
          {result && (
            <div className="w-full lg:w-1/3 bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 
                            rounded-2xl p-8 shadow-2xl animate-fade-in">
              <EmailResults domain={result.domain} emails={result.emails} />
            </div>
          )}

          {/* Tip card */}
          {result && (
            <div className="w-full lg:w-1/3 bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 
                            rounded-2xl p-8 shadow-2xl animate-fade-in">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <h2 className="text-lg font-semibold text-white">
                    Tip for Success
                  </h2>
                </div>
                
                <p className="text-sm text-zinc-400 leading-relaxed">
                  Paste all emails into the <span className="text-white font-medium">To:</span> field of your personal email (Gmail, Outlook, etc.). 
                  Hover over each address — the one with a <span className="text-emerald-400 font-medium">profile picture</span> is likely the valid email. 
                  Then send your message from your professional or school email.
                </p>

                {/* Tip image */}
                <div className="rounded-lg overflow-hidden border border-zinc-700 bg-zinc-800/50">
                  <img 
                    src="/Tip-image-example.png" 
                    alt="Example showing how to identify valid email by profile picture"
                    className="w-full h-auto"
                    onError={(e) => {
                      e.target.parentElement.style.display = 'none';
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-zinc-600 text-sm">
          <p>Free email domain lookup with caching</p>
        </div>
      </div>
    </main>
  );
}
