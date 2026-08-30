export default function Loading() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
      <div className="h-9 w-9 animate-spin rounded-full border-2 border-[var(--color-border-strong)] border-t-[var(--color-accent-light)]" />
      <p className="text-sm text-[var(--color-text-muted)]">
        Loading SentinelX…
      </p>
    </div>
  );
}
