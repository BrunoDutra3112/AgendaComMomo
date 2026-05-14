-- ============================================================
-- Nossa Agenda — Setup do banco de dados Supabase
-- Cole este conteúdo no SQL Editor do Supabase e clique em Run
-- ============================================================

-- Tabela de perfis (complementa auth.users)
create table if not exists public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  nome text not null,
  email text,
  created_at timestamptz default now()
);

-- Tabela de eventos
create table if not exists public.eventos (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  titulo text not null,
  descricao text,
  data_hora timestamptz not null,
  categoria text default 'outro',
  created_at timestamptz default now()
);

-- Habilitar Row Level Security
alter table public.profiles enable row level security;
alter table public.eventos enable row level security;

-- Policies para profiles
create policy "Usuários veem todos os perfis"
  on public.profiles for select
  using (true);

create policy "Usuário insere o próprio perfil"
  on public.profiles for insert
  with check (auth.uid() = id);

create policy "Usuário atualiza o próprio perfil"
  on public.profiles for update
  using (auth.uid() = id);

-- Policies para eventos
create policy "Todos os usuários autenticados veem os eventos"
  on public.eventos for select
  using (auth.role() = 'authenticated');

create policy "Usuário autenticado insere evento"
  on public.eventos for insert
  with check (auth.uid() = user_id);

create policy "Usuário deleta apenas seus eventos"
  on public.eventos for delete
  using (auth.uid() = user_id);

-- Índices para performance
create index if not exists idx_eventos_data_hora on public.eventos(data_hora);
create index if not exists idx_eventos_user_id on public.eventos(user_id);
