import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SentinelX — AI Governance Firewall",
    short_name: "SentinelX",
    description:
      "Enterprise AI Governance Firewall: detect, prevent, explain, and audit sensitive data leakage to large language models in real time.",
    start_url: "/",
    display: "standalone",
    background_color: "#09090b",
    theme_color: "#0b827a",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
