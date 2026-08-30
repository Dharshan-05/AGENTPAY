export interface Analyst {
  id: string;
  name: string;
  role: string;
  status: 'ONLINE' | 'AWAY' | 'OFFLINE';
  location: string;
  team: string;
  lastSeen: string;
  incident?: string | null;
  emoji?: string;
}

const ANALYSTS: Analyst[] = [
  { id: 'an-1', name: 'Aarav Mehta', role: 'Security Admin', status: 'ONLINE', location: 'Bengaluru', team: 'Governance', lastSeen: new Date().toISOString(), incident: 'INC-2026-0417', emoji: '🛡️' },
  { id: 'an-2', name: 'Priya Sharma', role: 'SOC Lead', status: 'ONLINE', location: 'Bengaluru', team: 'SOC', lastSeen: new Date().toISOString(), incident: 'INC-2026-0417', emoji: '🔍' },
  { id: 'an-3', name: 'Daniel Okafor', role: 'Security Engineer', status: 'ONLINE', location: 'Lagos', team: 'Engineering', lastSeen: new Date().toISOString(), incident: 'INC-2026-0418', emoji: '⚙️' },
  { id: 'an-4', name: 'Sofia Reyes', role: 'Compliance Officer', status: 'AWAY', location: 'Madrid', team: 'Compliance', lastSeen: new Date(Date.now() - 12 * 60000).toISOString(), incident: null, emoji: '📋' },
  { id: 'an-5', name: 'Kenji Watanabe', role: 'SOC Analyst', status: 'ONLINE', location: 'Tokyo', team: 'SOC', lastSeen: new Date().toISOString(), incident: 'INC-2026-0421', emoji: '🕵️' },
  { id: 'an-6', name: 'Maya Iyer', role: 'Threat Hunter', status: 'OFFLINE', location: 'Pune', team: 'Threat Intel', lastSeen: new Date(Date.now() - 3 * 3600 * 1000).toISOString(), incident: null, emoji: '🎯' },
];

const online = new Map<string, string>();

export function registerAnalyst(socketId: string, analystId: string): Analyst {
  online.set(socketId, analystId);
  const analyst = ANALYSTS.find((a) => a.id === analystId);
  if (analyst) {
    analyst.status = 'ONLINE';
    analyst.lastSeen = new Date().toISOString();
  }
  return analyst ?? ANALYSTS[0];
}

export function unregisterAnalyst(socketId: string): void {
  const analystId = online.get(socketId);
  online.delete(socketId);
  const analyst = ANALYSTS.find((a) => a.id === analystId);
  if (analyst && [...online.values()].every((v) => v !== analystId)) {
    analyst.status = 'AWAY';
    analyst.lastSeen = new Date().toISOString();
  }
}

export function getPresence(): Analyst[] {
  return ANALYSTS.map((a) => ({ ...a }));
}

export function analystRoster(): Analyst[] {
  return ANALYSTS;
}
