"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { motion } from "framer-motion";
import { Key, Copy, CheckCircle2, ShieldAlert, FileText, Zap } from "lucide-react";
import { api } from "@/lib/api";

export default function DeveloperPortal() {
  const { data: session } = useSession();
  const [keys, setKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState("");
  const [newKey, setNewKey] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (session) fetchKeys();
  }, [session]);

  const fetchKeys = async () => {
    try {
      const token = (session as any)?.accessToken;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
      const res = await fetch(`${apiUrl}/api/me/api-keys`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setKeys(data);
      } else {
        console.error('fetchKeys failed:', res.status);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createKey = async () => {
    try {
      setError(null);
      setLoading(true);
      const token = (session as any)?.accessToken;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
      const res = await fetch(`${apiUrl}/api/admin/api-keys`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ name: "Developer Key" })
      });
      if (res.ok) {
        const data = await res.json();
        setNewKey(data.apiKey);
        await fetchKeys();
      } else {
        const errData = await res.json().catch(() => ({}));
        const msg = errData?.error ?? `Request failed (${res.status})`;
        setError(msg);
        setLoading(false);
      }
    } catch (err) {
      console.error(err);
      setError('Network error — could not reach the API.');
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(text);
    setTimeout(() => setCopied(""), 2000);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Developer Portal</h1>
          <p className="text-sm text-text-muted mt-1">Manage your API keys and integrate with SentinelX</p>
        </div>
        <button
          onClick={createKey}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-light transition-colors"
        >
          <Key className="h-4 w-4" />
          Generate New Key
        </button>
      </div>

      {newKey && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-accent/20 bg-accent/5 p-6"
        >
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-accent/20 p-2 text-accent-light">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-text-primary">API Key Generated Successfully</h3>
              <p className="text-sm text-accent-light mb-4">{newKey.warning}</p>
              
              <div className="flex items-center gap-2 rounded-lg border border-border-subtle bg-bg-surface p-3 font-mono text-sm text-text-secondary">
                <span className="flex-1 overflow-x-auto">{newKey.secret}</span>
                <button
                  onClick={() => copyToClipboard(newKey.secret)}
                  className="rounded p-1.5 hover:bg-bg-primary text-text-muted hover:text-text-primary transition-colors"
                >
                  {copied === newKey.secret ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* API Keys List */}
          <div className="rounded-xl border border-border-subtle bg-bg-surface/50 backdrop-blur-sm overflow-hidden">
            <div className="border-b border-border-subtle p-4 bg-bg-surface/80">
              <h3 className="font-medium text-text-primary flex items-center gap-2">
                <Key className="h-4 w-4 text-text-muted" />
                Your Active API Keys
              </h3>
            </div>
            <div className="p-0">
              {error && (
                <div className="p-4 mx-4 mt-4 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
                  ⚠ {error}
                </div>
              )}
              {loading && !keys.length ? (
                <div className="p-8 text-center text-text-muted">Loading keys...</div>
              ) : keys.length === 0 ? (
                <div className="p-8 text-center flex flex-col items-center justify-center">
                  <Key className="h-8 w-8 text-text-dim mb-3" />
                  <p className="text-text-muted">No API keys found. Generate one to get started.</p>
                </div>
              ) : (
                <table className="w-full text-left text-sm">
                  <thead className="bg-bg-primary/50 text-text-muted">
                    <tr>
                      <th className="px-4 py-3 font-medium">Name</th>
                      <th className="px-4 py-3 font-medium">Prefix</th>
                      <th className="px-4 py-3 font-medium">Created</th>
                      <th className="px-4 py-3 font-medium">Last Used</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle">
                    {keys.map((key) => (
                      <tr key={key.id} className="hover:bg-bg-primary/50 transition-colors">
                        <td className="px-4 py-3 text-text-primary">{key.name}</td>
                        <td className="px-4 py-3 font-mono text-text-secondary">{key.keyPrefix}...</td>
                        <td className="px-4 py-3 text-text-secondary">
                          {new Date(key.createdAt).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-text-secondary">
                          {key.lastUsedAt ? new Date(key.lastUsedAt).toLocaleDateString() : 'Never'}
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-0.5 text-xs font-medium text-green-500">
                            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                            Active
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Quick Start Integration */}
          <div className="rounded-xl border border-border-subtle bg-bg-surface/50 backdrop-blur-sm overflow-hidden">
            <div className="border-b border-border-subtle p-4 bg-bg-surface/80 flex items-center justify-between">
              <h3 className="font-medium text-text-primary flex items-center gap-2">
                <FileText className="h-4 w-4 text-text-muted" />
                Quick Start: OpenAI Compatible Endpoint
              </h3>
            </div>
            <div className="p-4">
              <p className="text-sm text-text-secondary mb-4">
                SentinelX serves as an exact drop-in replacement for OpenAI. Simply change the base URL and use your SentinelX API key.
              </p>
              <div className="relative rounded-lg bg-[#0d0d12] p-4 font-mono text-sm overflow-hidden">
                <button
                  onClick={() => copyToClipboard(`curl https://YOUR-SENTINELX-API/v1/chat/completions \\
  -H "Authorization: Bearer sx_live_xxxxx" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "sentinel-auto",
    "messages": [{"role": "user", "content": "Explain JWT authentication."}]
  }'`)}
                  className="absolute right-2 top-2 rounded p-1.5 hover:bg-white/10 text-text-muted transition-colors"
                >
                  <Copy className="h-4 w-4" />
                </button>
                <div className="text-blue-400">curl <span className="text-green-400">https://YOUR-SENTINELX-API/v1/chat/completions</span> \</div>
                <div className="text-text-secondary pl-4">-H <span className="text-yellow-300">"Authorization: Bearer sx_live_xxxxx"</span> \</div>
                <div className="text-text-secondary pl-4">-H <span className="text-yellow-300">"Content-Type: application/json"</span> \</div>
                <div className="text-text-secondary pl-4">-d <span className="text-yellow-300">'{'{'}</span></div>
                <div className="text-text-secondary pl-8"><span className="text-purple-400">"model"</span>: <span className="text-yellow-300">"sentinel-auto"</span>,</div>
                <div className="text-text-secondary pl-8"><span className="text-purple-400">"messages"</span>: [{'{'}<span className="text-purple-400">"role"</span>: <span className="text-yellow-300">"user"</span>, <span className="text-purple-400">"content"</span>: <span className="text-yellow-300">"Explain JWT authentication."</span>{'}'}]</div>
                <div className="text-yellow-300 pl-4">{'}'}'</div>
              </div>
            </div>
          </div>
        </div>

        {/* Limits Sidebar */}
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-6 backdrop-blur-sm">
            <h3 className="font-medium text-text-primary flex items-center gap-2 mb-6">
              <Zap className="h-4 w-4 text-accent-light" />
              Your Usage Limits
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-text-secondary">Daily Tokens</span>
                  <span className="text-text-primary font-medium">100,000</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-bg-primary">
                  <div className="h-full bg-accent-light" style={{ width: '12%' }} />
                </div>
                <p className="text-xs text-text-muted mt-1.5">12,042 used today</p>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-text-secondary">Monthly Budget</span>
                  <span className="text-text-primary font-medium">$50.00</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-bg-primary">
                  <div className="h-full bg-green-500" style={{ width: '4%' }} />
                </div>
                <p className="text-xs text-text-muted mt-1.5">$2.14 spent this month</p>
              </div>

              <div className="pt-4 border-t border-border-subtle">
                <div className="flex justify-between text-sm py-2">
                  <span className="text-text-secondary">Rate Limit</span>
                  <span className="text-text-primary font-medium">20 req/min</span>
                </div>
                <div className="flex justify-between text-sm py-2">
                  <span className="text-text-secondary">Models</span>
                  <span className="text-text-primary font-medium text-right">GPT-4o-mini, Claude-3.5-sonnet</span>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-6 backdrop-blur-sm">
            <h3 className="font-medium text-text-primary flex items-center gap-2 mb-4">
              <ShieldAlert className="h-4 w-4 text-red-400" />
              Security Enforcement
            </h3>
            <p className="text-sm text-text-secondary mb-4">
              Your requests are automatically protected by SentinelX before reaching the LLM provider.
            </p>
            <ul className="space-y-2 text-sm text-text-secondary">
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Secret Blocking</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> PII Redaction</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Prompt Injection Blocking</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Prompt Optimization</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
