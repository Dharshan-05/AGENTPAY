"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, Shield, Key, TrendingUp, Settings, MoreVertical, CreditCard, Activity, CheckCircle2, XCircle, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/primitives";
import { getApiToken } from "@/lib/auth-token";

export default function AdminControlCenter() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const token = getApiToken();
      const res = await fetch("/api/admin/employees", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEmployees(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Admin Control Center</h1>
          <p className="text-sm text-text-muted mt-1">Manage employees, API keys, budgets, and security policies</p>
        </div>
        <button className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-light transition-colors">
          Add Employee
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3 text-text-muted mb-2">
            <Users className="h-4 w-4" />
            <span className="text-sm font-medium">Total Employees</span>
          </div>
          <div className="text-2xl font-semibold text-text-primary">{employees.length}</div>
        </div>
        <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3 text-text-muted mb-2">
            <Key className="h-4 w-4" />
            <span className="text-sm font-medium">Active API Keys</span>
          </div>
          <div className="text-2xl font-semibold text-text-primary">{employees.reduce((acc, e) => acc + (e.apiKeys || 0), 0)}</div>
        </div>
        <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3 text-text-muted mb-2">
            <Activity className="h-4 w-4" />
            <span className="text-sm font-medium">Requests Today</span>
          </div>
          <div className="text-2xl font-semibold text-text-primary">{employees.reduce((acc, e) => acc + (e.requestsToday || 0), 0)}</div>
        </div>
        <div className="rounded-xl border border-border-subtle bg-bg-surface/50 p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3 text-text-muted mb-2">
            <CreditCard className="h-4 w-4" />
            <span className="text-sm font-medium">Spend Today</span>
          </div>
          <div className="text-2xl font-semibold text-text-primary">
            ${employees.reduce((acc, e) => acc + (e.costToday || 0), 0).toFixed(4)}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border-subtle bg-bg-surface/50 backdrop-blur-sm overflow-hidden">
        <div className="border-b border-border-subtle p-4 bg-bg-surface/80 flex items-center justify-between">
          <h3 className="font-medium text-text-primary">Employee Governance</h3>
          <div className="flex items-center gap-2">
            <input 
              type="text" 
              placeholder="Search employees..." 
              className="rounded-lg border border-border-subtle bg-bg-primary/50 px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent"
            />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-text-muted">Loading employees...</div>
          ) : (
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-bg-primary/50 text-text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Employee</th>
                  <th className="px-4 py-3 font-medium">Keys</th>
                  <th className="px-4 py-3 font-medium">Token Limits (D/M)</th>
                  <th className="px-4 py-3 font-medium">Budget (D/M)</th>
                  <th className="px-4 py-3 font-medium">Usage Today</th>
                  <th className="px-4 py-3 font-medium">Models</th>
                  <th className="px-4 py-3 font-medium">Security</th>
                  <th className="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-bg-primary/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex flex-col">
                        <span className="font-medium text-text-primary">{emp.name}</span>
                        <span className="text-xs text-text-secondary">{emp.email}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded bg-bg-primary px-2 py-0.5 text-xs text-text-secondary border border-border-subtle">
                        {emp.apiKeys} active
                      </span>
                    </td>
                    <td className="px-4 py-3 text-text-secondary">
                      {emp.dailyTokenLimit ? emp.dailyTokenLimit.toLocaleString() : 'Unl'} / {emp.monthlyTokenLimit ? emp.monthlyTokenLimit.toLocaleString() : 'Unl'}
                    </td>
                    <td className="px-4 py-3 text-text-secondary">
                      ${emp.dailyBudget || '0'} / ${emp.monthlyBudget || '0'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-bg-primary">
                            <div className="h-full bg-accent-light" style={{ width: `${Math.min(100, ((emp.tokensToday||0) / (emp.dailyTokenLimit||100000)) * 100)}%` }} />
                          </div>
                          <span className="text-xs text-text-secondary">{emp.tokensToday?.toLocaleString() || 0} tkns</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-bg-primary">
                            <div className="h-full bg-green-500" style={{ width: `${Math.min(100, ((emp.costToday||0) / (emp.dailyBudget||5)) * 100)}%` }} />
                          </div>
                          <span className="text-xs text-text-secondary">${(emp.costToday||0).toFixed(3)}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <Badge variant="outline" className="text-[10px] border-green-500/30 text-green-400">✓ GPT-4o-mini</Badge>
                        <Badge variant="outline" className="text-[10px] border-green-500/30 text-green-400">✓ Claude</Badge>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1.5 text-text-muted">
                        <span title="Secret Blocking"><CheckCircle2 className="h-4 w-4 text-green-500" /></span>
                        <span title="PII Redaction"><CheckCircle2 className="h-4 w-4 text-green-500" /></span>
                        <span title="Prompt Injection"><CheckCircle2 className="h-4 w-4 text-green-500" /></span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button className="rounded p-1.5 text-text-muted hover:bg-bg-primary hover:text-text-primary transition-colors">
                        <Settings className="h-4 w-4" />
                      </button>
                      <button className="rounded p-1.5 text-text-muted hover:bg-bg-primary hover:text-text-primary transition-colors ml-1">
                        <MoreVertical className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
                {employees.length === 0 && !loading && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-text-muted">
                      No employees found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
