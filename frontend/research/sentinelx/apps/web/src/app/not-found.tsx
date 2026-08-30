import Link from "next/link";
import { Shield, SearchX } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-[var(--color-border-strong)] bg-[var(--color-bg-elevated)] shadow-[var(--shadow-card)]">
        <SearchX className="h-7 w-7 text-[var(--color-text-secondary)]" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
          404 — Route not found
        </h2>
        <p className="mt-1 max-w-md text-sm text-[var(--color-text-secondary)]">
          The page you are looking for does not exist, or it may have been
          moved behind a different role.
        </p>
      </div>
      <Link
        href="/"
        className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-accent-dark)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--color-accent)]"
      >
        <Shield className="h-4 w-4" />
        Back to dashboard
      </Link>
    </div>
  );
}
