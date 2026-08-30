import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the Carina command center", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Carina — AI Command Center Demo<\/title>/i);
  assert.match(html, /HOSTED DEMO/);
  assert.match(html, /LOCAL LIVE/);
  assert.match(html, /CARINA VOICE · DEMO CONTROL/);
  assert.match(html, /AGENT CONCEPTS/);
  assert.match(html, /SYSTEMS ENGINE/);
  assert.match(html, /Preview demo listening animation/);
  assert.match(html, /no microphone or agent backend connected/i);
  assert.doesNotMatch(html, />\s*LIVE\s*</i);
  assert.doesNotMatch(html, /\$\d/);
});

test("keeps interaction and accessibility controls in source", async () => {
  const [page, css, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
  ]);

  assert.match(page, /useState/);
  assert.match(page, /"Preview demo listening animation"/);
  assert.match(page, /aria-label=\{`Message \$\{selectedAgent\}`\}/);
  assert.match(page, /LOCAL LIVE/);
  assert.match(page, /Not configured/);
  assert.doesNotMatch(page, /4 agents online/);
  assert.doesNotMatch(page, /Connected · Leandro/);
  assert.doesNotMatch(page, /TOTAL TOKEN VALUE/);
  assert.match(css, /prefers-reduced-motion:\s*reduce/);
  assert.match(layout, /title:\s*"Carina — AI Command Center Demo"/);
});
