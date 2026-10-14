import React from 'react';
import { Cpu, CheckCircle2, AlertCircle, Sparkles, BookOpen, Layers } from 'lucide-react';

export default function Header({ health, isDarkTheme, setIsDarkTheme }) {
  const isConnected = health?.mcp_server_connected;
  const tools = health?.discovered_tools || [];

  return (
    <header className="h-14 bg-slate-950 border-b border-slate-800 px-4 flex items-center justify-between select-none shrink-0 z-20">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-white tracking-wide text-sm sm:text-base">PyTutor</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              MCP v2.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            Intelligent Tutoring System with Scaffolding Pedagogy
          </p>
        </div>
      </div>

      {/* Center: Discovered MCP Tools Badges */}
      <div className="hidden lg:flex items-center space-x-2 bg-slate-900/80 px-3 py-1 rounded-lg border border-slate-800 text-xs text-slate-300">
        <span className="text-slate-400 flex items-center space-x-1 font-mono text-[11px]">
          <Layers className="w-3.5 h-3.5 text-emerald-400" />
          <span>MCP Tools ({tools.length}):</span>
        </span>
        <div className="flex items-center space-x-1.5">
          {tools.length > 0 ? (
            tools.map((tool) => (
              <span
                key={tool}
                className="font-mono text-[10.5px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700/60 text-slate-300"
              >
                {tool}
              </span>
            ))
          ) : (
            <span className="text-slate-500 text-[11px] italic">Đang khám phá qua stdio...</span>
          )}
        </div>
      </div>

      {/* Right: Health Status & Theme Toggle */}
      <div className="flex items-center space-x-3">
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            isConnected
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
          }`}
          title={isConnected ? 'MCP Server kết nối thành công' : 'Chưa kết nối tới Backend / MCP Server'}
        >
          {isConnected ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 animate-pulse" />
              <span>MCP Online</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5" />
              <span>MCP Offline</span>
            </>
          )}
        </div>

        <button
          onClick={() => setIsDarkTheme(!isDarkTheme)}
          className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition-colors"
          title="Đổi giao diện Editor Dark / Light"
        >
          {isDarkTheme ? '🌙 Dark' : '☀️ Light'}
        </button>
      </div>
    </header>
  );
}
