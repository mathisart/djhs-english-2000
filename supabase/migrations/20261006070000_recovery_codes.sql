alter table public.players add column if not exists recovery_code_hash text;
create unique index if not exists players_recovery_code_hash_idx
  on public.players (recovery_code_hash)
  where recovery_code_hash is not null;
