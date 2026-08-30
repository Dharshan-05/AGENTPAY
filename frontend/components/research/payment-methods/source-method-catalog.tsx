'use client';

import { CatalogMethodTypeRecord } from './source-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface SourceMethodCatalogProps {
  types: CatalogMethodTypeRecord[];
}

export function SourceMethodCatalog({ types }: SourceMethodCatalogProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
      {types.map((cat) => (
        <div key={cat.type} className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-purple-400 font-bold tracking-wider">{cat.type}</span>
              <AGBadge status={cat.availability} size="sm" />
            </div>
            <h4 className="font-bold text-slate-100 text-sm font-display">{cat.label}</h4>
            <p className="text-[11px] text-slate-400 font-sans">{cat.description}</p>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-white/[0.06] text-[10px]">
            <div className="flex justify-between">
              <span className="text-slate-500">Verification:</span>
              <span className="text-slate-300 font-bold">{cat.verificationMethod}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">PCI Scope:</span>
              <span className="text-emerald-400 font-bold">{cat.pciScope}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Processors:</span>
              <span className="text-blue-400 font-bold">{cat.supportedProcessors.join(', ')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Currencies:</span>
              <span className="text-slate-300">{cat.supportedCurrencies.join(', ')}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
