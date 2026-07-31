"use client";

import { useState } from "react";
import { useMantisStore } from "@/lib/store";
import { Badge } from "@/components/ui/badge";

export function Header() {
  const alertCount = useMantisStore((s) => s.alertCount);
  const sidebarOpen = useMantisStore((s) => s.sidebarOpen);
  const toggleSidebar = useMantisStore((s) => s.toggleSidebar);
  const [searchFocused, setSearchFocused] = useState(false);

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200/80 bg-white/80 backdrop-blur-md px-6 sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="rounded-xl p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all duration-200 hover:scale-105 active:scale-95"
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? (
            <PanelLeftCloseIcon className="h-5 w-5" />
          ) : (
            <MenuIcon className="h-5 w-5" />
          )}
        </button>

        {/* Search Bar */}
        <div className={`relative transition-all duration-300 ${searchFocused ? "w-80" : "w-64"}`}>
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search assets, alerts, work orders..."
            className="w-full rounded-xl border border-gray-200 bg-gray-50/50 py-2 pl-10 pr-4 text-sm text-gray-700 placeholder:text-gray-400 transition-all duration-200 focus:bg-white focus:border-mantis-300 focus:ring-2 focus:ring-mantis-100 focus:outline-none"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex h-5 items-center gap-1 rounded border border-gray-200 bg-gray-100 px-1.5 text-[10px] font-medium text-gray-400">
            ⌘K
          </kbd>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Alert Badge */}
        {alertCount > 0 && (
          <Badge variant="destructive" className="gap-1.5 px-3 py-1 animate-fade-in hover:scale-105 transition-transform cursor-pointer shadow-sm shadow-red-200">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-white" />
            </span>
            {alertCount} active
          </Badge>
        )}

        {/* Notification Bell */}
        <button className="relative rounded-xl p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all duration-200 hover:scale-105 active:scale-95">
          <BellIcon className="h-5 w-5" />
          {alertCount > 0 && (
            <span className="absolute top-1 right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500" />
            </span>
          )}
        </button>

        {/* Divider */}
        <div className="h-8 w-px bg-gray-200" />

        {/* System Status */}
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-1.5 transition-colors hover:bg-emerald-100 cursor-default">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-xs font-medium text-emerald-700">Online</span>
        </div>

        {/* User Avatar */}
        <button className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-mantis-500 to-mantis-700 text-xs font-bold text-white shadow-md shadow-mantis-200 transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-mantis-200 active:scale-95">
          OP
        </button>
      </div>
    </header>
  );
}

function MenuIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <line x1="4" x2="20" y1="12" y2="12" /><line x1="4" x2="20" y1="6" y2="6" /><line x1="4" x2="20" y1="18" y2="18" />
    </svg>
  );
}

function PanelLeftCloseIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <rect width="18" height="18" x="3" y="3" rx="2" /><path d="M9 3v18" /><path d="m16 15-3-3 3-3" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
    </svg>
  );
}

function BellIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </svg>
  );
}
