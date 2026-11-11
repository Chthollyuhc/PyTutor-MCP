import React from 'react';
import { ChevronLeft, ChevronRight, Search } from 'lucide-react';

export const TABLE_PAGE_SIZE = 10;

export function getPage(items, requestedPage) {
  const pageCount = Math.max(1, Math.ceil(items.length / TABLE_PAGE_SIZE));
  const page = Math.min(Math.max(1, requestedPage), pageCount);
  const startIndex = (page - 1) * TABLE_PAGE_SIZE;
  return {
    items: items.slice(startIndex, startIndex + TABLE_PAGE_SIZE),
    page,
    pageCount,
    startIndex,
  };
}

export function TableLoading({ label }) {
  return (
    <div role="status" aria-label={label} className="space-y-3 p-4">
      <span className="sr-only">{label}</span>
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index} className="flex items-center gap-4 border-b border-slate-800 pb-3 last:border-0">
          <span className="h-3 w-10 animate-pulse rounded bg-slate-700" />
          <span className="h-3 flex-1 animate-pulse rounded bg-slate-800" />
          <span className="h-3 w-24 animate-pulse rounded bg-slate-700" />
        </div>
      ))}
    </div>
  );
}

export default function TableControls({
  label,
  query,
  onQueryChange,
  placeholder,
  total,
  page,
  pageCount,
  onPageChange,
}) {
  const pageStart = total === 0 ? 0 : (page - 1) * TABLE_PAGE_SIZE + 1;
  const pageEnd = Math.min(page * TABLE_PAGE_SIZE, total);

  return (
    <div className="flex flex-col gap-3 border-b border-slate-800 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <label className="relative block w-full sm:max-w-sm">
        <span className="sr-only">{label}</span>
        <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder={placeholder}
          aria-label={label}
          className="min-h-10 w-full rounded-lg border border-slate-700 bg-slate-950 py-2 pl-9 pr-3 text-sm text-slate-100 placeholder:text-slate-400 outline-none transition-colors duration-200 focus-visible:border-emerald-400 focus-visible:ring-2 focus-visible:ring-emerald-400/25"
        />
      </label>

      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300 sm:justify-end">
        <span aria-live="polite" className="tabular-nums">
          {total === 0 ? 'Không có kết quả phù hợp' : `Hiển thị ${pageStart}–${pageEnd} / ${total}`}
        </span>
        <div role="group" aria-label={`Phân trang: ${label}`} className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            aria-label="Trang trước"
            className="inline-flex size-9 items-center justify-center rounded-lg border border-slate-700 text-slate-200 transition-colors hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:pointer-events-none disabled:text-slate-500"
          >
            <ChevronLeft aria-hidden="true" className="size-4" />
          </button>
          <span className="min-w-14 text-center font-medium tabular-nums">{page} / {pageCount}</span>
          <button
            type="button"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= pageCount}
            aria-label="Trang sau"
            className="inline-flex size-9 items-center justify-center rounded-lg border border-slate-700 text-slate-200 transition-colors hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:pointer-events-none disabled:text-slate-500"
          >
            <ChevronRight aria-hidden="true" className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
