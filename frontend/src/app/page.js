"use client";

import { useState } from "react";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  
  // Form state
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [company, setCompany] = useState("");

  const handleGenerate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

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

  const handleCopyAll = async () => {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result.emails.join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleOpenEmail = () => {
    if (!result) return;
    const mailtoLink = `mailto:${result.emails.join(",")}`;
    window.location.href = mailtoLink;
  };

  return (
    <main className="min-h-screen bg-zinc-950 relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-zinc-900 via-zinc-950 to-zinc-900" />
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
      
      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3 tracking-tight">
            Email <span className="text-emerald-400">Finder</span>
          </h1>
          <p className="text-zinc-400 text-lg max-w-lg mx-auto">
            Find anyone&apos;s email address by entering their name and company.
          </p>
        </div>

        {/* Main card with two columns */}
        <div className="max-w-4xl mx-auto bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden">
          <div className="flex flex-col md:flex-row">
            
            {/* Left side - Form */}
            <div className="w-full md:w-1/2 p-8 border-b md:border-b-0 md:border-r border-zinc-800">
              <form onSubmit={handleGenerate} className="space-y-5">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">
                    First name
                  </label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Tim"
                    required
                    className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                               text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                               focus:ring-emerald-500 focus:border-transparent transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">
                    Last name
                  </label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Cook"
                    required
                    className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                               text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                               focus:ring-emerald-500 focus:border-transparent transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">
                    Company
                  </label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="SpaceX"
                    required
                    className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                               text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                               focus:ring-emerald-500 focus:border-transparent transition-all"
                  />
                </div>

                {error && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 px-6 bg-emerald-600 hover:bg-emerald-500 
                             disabled:bg-zinc-700 disabled:cursor-not-allowed
                             text-white font-semibold rounded-lg transition-all duration-200
                             shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30
                             uppercase tracking-wide text-sm"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle 
                          className="opacity-25" 
                          cx="12" cy="12" r="10" 
                          stroke="currentColor" 
                          strokeWidth="4"
                          fill="none"
                        />
                        <path 
                          className="opacity-75" 
                          fill="currentColor" 
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Searching...
                    </span>
                  ) : (
                    "Generate Email Addresses"
                  )}
                </button>
              </form>
            </div>

            {/* Right side - Results */}
            <div className="w-full md:w-1/2 p-8 bg-zinc-800/30">
              {result ? (
                <div className="space-y-4">
                  {/* Email list */}
                  <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg overflow-hidden">
                    <div className="max-h-[360px] overflow-y-auto p-4 space-y-1">
                      {result.emails.map((email, index) => (
                        <div 
                          key={index}
                          className="text-sm font-mono text-zinc-300 py-1.5 px-2 rounded
                                     hover:bg-zinc-700/50 transition-colors cursor-default"
                        >
                          {email}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Footer with count and actions */}
                  <div className="flex items-center justify-between text-sm text-zinc-400">
                    <span>{result.emails.length} emails generated</span>
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={handleCopyAll}
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1"
                      >
                        {copied ? (
                          <>
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            Copied!
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            Copy All
                          </>
                        )}
                      </button>
                      <span className="text-zinc-600">—</span>
                      <button 
                        onClick={handleOpenEmail}
                        className="hover:text-emerald-400 transition-colors"
                      >
                        Open in Gmail
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center min-h-[300px]">
                  <div className="text-center text-zinc-500">
                    <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <p>Enter a name and company to generate email addresses</p>
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Tip section below */}
        {result && (
          <div className="max-w-4xl mx-auto mt-6 bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-xl p-6">
            <div className="flex flex-col md:flex-row items-start gap-6">
              <div className="flex items-start gap-3 flex-1">
                <svg className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <div>
                  <h3 className="text-white font-medium mb-1">Tip for Success</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    Paste all emails into the <span className="text-white font-medium">To:</span> field of your personal email. 
                    Hover over each address — the one with a <span className="text-emerald-400 font-medium">profile picture</span> is likely the valid email.
                  </p>
                </div>
              </div>
              {/* Tip image */}
              <div className="w-full md:w-64 flex-shrink-0 rounded-lg overflow-hidden border border-zinc-700 bg-zinc-800/50">
                <img 
                  src="/Tip-image-example.png" 
                  alt="Example showing how to identify valid email by profile picture"
                  className="w-full h-auto"
                />
              </div>
            </div>
          </div>
        )}

        {/* Trusted By Section */}
        <div className="mt-16 pt-10 border-t border-zinc-800">
          <p className="text-center text-zinc-500 text-sm mb-8">
            Trusted by students and professionals at
          </p>
          
          {/* Scrolling logo marquee */}
          <div className="relative overflow-hidden">
            {/* Gradient fade edges */}
            <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-zinc-950 to-transparent z-10"></div>
            <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-zinc-950 to-transparent z-10"></div>
            
            {/* Scrolling container */}
            <div className="flex animate-marquee">
              {/* First set of logos */}
              <div className="flex items-center gap-16 px-8 shrink-0">
                <img src="/logos/berkeley.png" alt="UC Berkeley" className="h-8 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/amazon.png" alt="Amazon" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/agi.png" alt="AGI Inc" className="h-8 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/apollo.png" alt="Apollo.ai" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/langchain.png" alt="LangChain" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/llamaindex.png" alt="LlamaIndex" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
              </div>
              {/* Duplicate set for seamless loop */}
              <div className="flex items-center gap-16 px-8 shrink-0">
                <img src="/logos/berkeley.png" alt="UC Berkeley" className="h-8 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/amazon.png" alt="Amazon" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/agi.png" alt="AGI Inc" className="h-8 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/apollo.png" alt="Apollo.ai" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/langchain.png" alt="LangChain" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
                <img src="/logos/llamaindex.png" alt="LlamaIndex" className="h-7 w-auto object-contain brightness-0 invert opacity-50" />
              </div>
            </div>
          </div>
        </div>

        {/* Footer spacer */}
        <div className="pb-8"></div>
      </div>
    </main>
  );
}
