# Supabase Audit Reference

Run these in the Supabase SQL editor (or `psql`) for the user's own project. Also check the dashboard's Security Advisor if available.

## 1. Tables without RLS

```sql
select n.nspname as schema,
       c.relname as table_name,
       c.relrowsecurity as rls_enabled
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where c.relkind in ('r', 'p')
  and n.nspname = 'public'          -- add any other schema exposed through the API
order by rls_enabled, table_name;
```

Every row must show `rls_enabled = true`. RLS enabled with **no** policies means nobody (except the service role) can access the table — safe, but the app may break.

## 2. All policies

```sql
select tablename, policyname, roles, cmd, qual as using_expr, with_check
from pg_policies
where schemaname = 'public'
order by tablename, cmd;
```

Red flags:
- `using (true)` on SELECT for tables with private data.
- `with check (true)` on INSERT/UPDATE.
- Write policies for `anon` or `public` roles.
- `auth.uid() is not null` / `auth.role() = 'authenticated'` as the only condition — any signed-up user (and signup is usually open) sees every row.
- Role checks based on `auth.jwt() -> 'user_metadata'` — **users can edit their own user_metadata**. Use `app_metadata` (set server-side) or a roles table.
- UPDATE policies without `with check` — users can move a row to another owner.

## 3. Views that bypass RLS

Views run with the owner's privileges by default and skip RLS on underlying tables.

```sql
select c.relname as view_name, c.reloptions
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where c.relkind = 'v' and n.nspname = 'public';
```

Fix (Postgres 15+): `alter view public.my_view set (security_invoker = true);` — or move the view out of the exposed schema.

## 4. SECURITY DEFINER functions callable via RPC

```sql
select p.proname, p.prosecdef as security_definer, p.proconfig
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.prosecdef = true;
```

For each: does it check `auth.uid()` before acting? Is `search_path` set (`set search_path = ''`)? If it should not be public: `revoke execute on function public.fn_name from anon, authenticated;`

## 5. Storage

```sql
select id, name, public from storage.buckets;
select policyname, cmd, roles, qual, with_check
from pg_policies where schemaname = 'storage' and tablename = 'objects';
```

- Public buckets: anyone with the URL can read every file. Only for genuinely public assets.
- Private buckets: policies should scope by owner, e.g. a folder per user: `(storage.foldername(name))[1] = (select auth.uid())::text`.

## 6. Column-level escalation

RLS controls rows, not columns. If users can update their own `profiles` row and that row has `role`, `plan`, `credits` or `is_admin`, they can promote themselves. Fixes:
- Keep privileged fields in a separate table with no user write policy, or
- Revoke column update privileges: `revoke update (role, plan) on public.profiles from authenticated;`, or
- A trigger that rejects changes to those columns unless done by the service role.

## Good baseline policies

```sql
alter table public.profiles enable row level security;

create policy "profiles: owner can read"
  on public.profiles for select to authenticated
  using ((select auth.uid()) = id);

create policy "profiles: owner can update"
  on public.profiles for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- Owned rows in another table
alter table public.orders enable row level security;

create policy "orders: owner can read"
  on public.orders for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "orders: owner can insert own"
  on public.orders for insert to authenticated
  with check ((select auth.uid()) = user_id);
```

Wrapping `auth.uid()` in `(select ...)` lets Postgres cache it per query (performance). Index the owner column (`create index on public.orders (user_id);`).

Multi-tenant apps: check membership through a join table, e.g. `using (exists (select 1 from public.memberships m where m.org_id = orders.org_id and m.user_id = (select auth.uid())))`.

## Live verification (own project only)

With the **anon** key, which is safe to use for this test:

```bash
curl "https://<project-ref>.supabase.co/rest/v1/<table>?select=*&limit=5" \
  -H "apikey: <anon-key>" -H "Authorization: Bearer <anon-key>"
```

Private tables should return `[]` or an error. Then sign in as test user A and confirm user B's rows are not returned.
