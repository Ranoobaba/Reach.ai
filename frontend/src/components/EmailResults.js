"use client";

import { useState } from "react";

export default function EmailResults({ domain, emails }) {
  const [copied, setCopied] = useState(false);

  const handleCopyAll = async () => {
    try {
      await navigator.clipboard.writeText(emails.join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleOpenEmail = () => {
    // Create mailto link with all emails in the "to" field
    const mailtoLink = `mailto:${emails.join(",")}`;
    window.location.href = mailtoLink;
  };

  return (
    <div className="w-full max-w-md space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">
            Generated Emails
          </h2>
          <p className="text-sm text-zinc-400">
            Domain found: <span className="text-emerald-400 font-mono">{domain}</span>
          </p>
        </div>
        <span className="text-sm text-zinc-500">
          {emails.length} emails
        </span>
      </div>

      <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg overflow-hidden">
        <div className="max-h-80 overflow-y-auto p-4 space-y-1">
          {emails.map((email, index) => (
            <div 
              key={index}
              className="text-sm font-mono text-zinc-300 py-1 px-2 rounded
                         hover:bg-zinc-700/50 transition-colors cursor-default"
            >
              {email}
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleCopyAll}
          className="flex-1 py-2.5 px-4 bg-zinc-700 hover:bg-zinc-600 
                     text-white font-medium rounded-lg transition-all duration-200
                     flex items-center justify-center gap-2"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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

        <button
          onClick={handleOpenEmail}
          className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 
                     text-white font-medium rounded-lg transition-all duration-200
                     shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30
                     flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Open in Email
        </button>
      </div>

    </div>
  );
}

