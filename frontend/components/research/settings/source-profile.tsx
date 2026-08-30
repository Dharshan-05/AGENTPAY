'use client';

import { UserProfile } from './source-types';
import { User, Mail, Shield, Clock } from 'lucide-react';
import { useState } from 'react';

interface SourceProfileProps {
  profile: UserProfile;
}

export function SourceProfile({ profile }: SourceProfileProps) {
  const [name, setName] = useState(profile.fullName);
  const [email, setEmail] = useState(profile.email);

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <User className="w-4 h-4 text-blue-600" />
            Account Profile & Identity
          </h3>
          <p className="text-xs text-slate-500">Excavated account profile settings form</p>
        </div>
      </div>

      <div className="space-y-4 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Assigned Role</label>
            <div className="px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl font-bold text-blue-700">
              {profile.role}
            </div>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Timezone</label>
            <div className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-700">
              {profile.timezone}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
