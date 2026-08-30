"use client";

export default function GlobalError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  return (
    <html lang="en">
      <body style={{ background: "#09090b", color: "#fafafa" }}>
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 16,
            padding: 24,
            textAlign: "center",
            fontFamily: "ui-sans-serif, system-ui, sans-serif",
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#1c1c21",
              border: "1px solid rgba(255,255,255,0.12)",
            }}
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: 0 }}>
            Critical failure
          </h1>
          <p style={{ color: "#a1a1aa", fontSize: 14, margin: 0, maxWidth: 420 }}>
            SentinelX encountered a fatal error{error.digest ? ` (ref ${error.digest.slice(0, 8)})` : ""}. The error has been recorded.
          </p>
          <button
            onClick={unstable_retry}
            style={{
              marginTop: 8,
              padding: "10px 18px",
              borderRadius: 10,
              border: "1px solid rgba(11,130,122,0.35)",
              background: "#08534e",
              color: "#fff",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
