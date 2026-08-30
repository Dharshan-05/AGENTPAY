"use client";

import { useEffect } from "react";
import Link from "next/link";
import { ShieldAlert, RotateCcw } from "lucide-react";

export default function Error({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-[var(--color-border-strong)] bg-[var(--color-bg-elevated)] shadow-[var(--shadow-card)]">
        <ShieldAlert className="h-7 w-7 text-[var(--color-status-high)]" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
          Something went wrong
        </h2>
        <p className="mt-1 max-w-md text-sm text-[var(--color-text-secondary)]">
          SentinelX hit an unexpected error while rendering this page
          {error.digest ? (
            <>
              {" "}
              <span className="font-mono text-[var(--color-text-muted)]">
                (ref {error.digest.slice(0, 8)})
              </span>
            </>
          ) : null}
          .
        </p>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={unstable_retry}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-accent-dark)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--color-accent)]"
        >
          <RotateCcw className="h-4 w-4" />
          Try again
        </button>
        <Link
          href="/"
          className="inline-flex items-center rounded-lg border border-[var(--color-border-default)] px-4 py-2 text-sm font-medium text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-strong)] hover:text-[var(--color-text-primary)]"
        >
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
