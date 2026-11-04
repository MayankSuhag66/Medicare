-- Run once in the Supabase SQL Editor. Original files are never stored.
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  kind text not null check (kind in ('forms', 'prescriptions', 'reports')),
  name text not null,
  extracted_text text not null,
  result jsonb not null default '{}'::jsonb,
  ai_analyzed boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists documents_user_created_idx on public.documents (user_id, created_at desc);

alter table public.documents enable row level security;

revoke all on public.documents from anon;
grant select, insert, update, delete on public.documents to authenticated;

create policy "Users read only their own documents" on public.documents
  for select to authenticated using ((select auth.uid()) = user_id);

create policy "Users insert only their own documents" on public.documents
  for insert to authenticated with check ((select auth.uid()) = user_id);

create policy "Users edit only their own documents" on public.documents
  for update to authenticated using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "Users delete only their own documents" on public.documents
  for delete to authenticated using ((select auth.uid()) = user_id);
