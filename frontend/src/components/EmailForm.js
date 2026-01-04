"use client";

import { useState } from "react";

export default function EmailForm({ onGenerate, isLoading }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [company, setCompany] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate({ firstName, lastName, company });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md space-y-6">
      <div className="space-y-2">
        <label 
          htmlFor="firstName" 
          className="block text-sm font-medium text-zinc-300"
        >
          First Name
        </label>
        <input
          id="firstName"
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          placeholder="John"
          required
          className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                     text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                     focus:ring-emerald-500 focus:border-transparent transition-all"
        />
      </div>

      <div className="space-y-2">
        <label 
          htmlFor="lastName" 
          className="block text-sm font-medium text-zinc-300"
        >
          Last Name
        </label>
        <input
          id="lastName"
          type="text"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          placeholder="Doe"
          required
          className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                     text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                     focus:ring-emerald-500 focus:border-transparent transition-all"
        />
      </div>

      <div className="space-y-2">
        <label 
          htmlFor="company" 
          className="block text-sm font-medium text-zinc-300"
        >
          Company
        </label>
        <input
          id="company"
          type="text"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="OpenAI"
          required
          className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg 
                     text-white placeholder-zinc-500 focus:outline-none focus:ring-2 
                     focus:ring-emerald-500 focus:border-transparent transition-all"
        />
        <p className="text-xs text-zinc-500 mt-1">
          <span className="text-red-400 line-through">Nixo</span> → <span className="text-emerald-400">Nixo (YC S25)</span> — Use the company&apos;s full name for accurate results
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-6 bg-emerald-600 hover:bg-emerald-500 
                   disabled:bg-zinc-700 disabled:cursor-not-allowed
                   text-white font-semibold rounded-lg transition-all duration-200
                   shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30"
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
  );
}

