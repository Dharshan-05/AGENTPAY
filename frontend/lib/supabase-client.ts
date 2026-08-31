import { createClient } from '@supabase/supabase-js';

const supabaseUrl =
  process.env.NEXT_PUBLIC_SUPABASE_URL ||
  process.env.VITE_SUPABASE_URL ||
  'https://qlocrlukwwdddbpbgglm.supabase.co';

const supabaseAnonKey =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ||
  'sb_publishable_OFq5KXbecUXnNNCq_ZbgCg_ZffDDHGN';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
