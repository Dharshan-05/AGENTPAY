'use client';

import React from 'react';

interface Column<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (row: T) => React.ReactNode;
}

interface AGTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  selectedId?: string;
  idKey?: keyof T;
}

export function AGTable<T>({
  columns,
  data,
  onRowClick,
  selectedId,
  idKey = 'id' as keyof T,
}: AGTableProps<T>) {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-slate-900/60 overflow-hidden backdrop-blur-xl font-mono text-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/60 text-slate-400 text-[10px] uppercase tracking-wider">
              {columns.map((col, idx) => (
                <th key={idx} className="p-3.5 font-semibold">
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {data.map((row, rIdx) => {
              const rowId = String(row[idKey] ?? rIdx);
              const isSelected = selectedId === rowId;
              return (
                <tr
                  key={rowId}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`transition-colors ${
                    onRowClick ? 'cursor-pointer' : ''
                  } ${
                    isSelected
                      ? 'bg-emerald-500/10 border-l-2 border-l-emerald-400'
                      : 'hover:bg-slate-800/40'
                  }`}
                >
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} className="p-3.5">
                      {col.cell
                        ? col.cell(row)
                        : String(col.accessorKey ? row[col.accessorKey] : '')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
