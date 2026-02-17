# 数据表
## comments
### sql
```sql
create table public.comments (
  id uuid not null default gen_random_uuid (),
  post_id uuid not null,
  author_id uuid not null,
  content text not null,
  created_at timestamp with time zone null default now(),
  constraint comments_pkey primary key (id),
  constraint comments_author_id_fkey foreign KEY (author_id) references profiles (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "admin full access" ON public.comments
  AS PERMISSIVE
  USING ((EXISTS ( SELECT 1
   FROM profiles
  WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));

CREATE POLICY "author insert" ON public.comments
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = author_id));

CREATE POLICY "author update" ON public.comments
  AS PERMISSIVE FOR UPDATE
  USING ((auth.uid() = author_id));

CREATE POLICY "public read" ON public.comments
  AS PERMISSIVE FOR SELECT
  USING (true);

## words
### sql
```sql
create table public.words (
  word_id uuid not null default gen_random_uuid (),
  author_id uuid not null,
  tags jsonb not null default '[]'::jsonb,
  word_url text not null,
  category text not null,
  status public.word_status not null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  word_name text null,
  constraint words_pkey primary key (word_id),
  constraint words_author_id_fkey foreign KEY (author_id) references profiles (id),
  constraint words_word_name_check check ((length(word_name) <= 25))
) TABLESPACE pg_default;

create trigger word_status_transition_trigger BEFORE
update OF status on words for EACH row
execute FUNCTION enforce_word_status_transition ();
```
### migration
```sql
-- WordTag = {id: text, display_content: text, create_time: bigint}
ALTER TABLE public.words
  ALTER COLUMN tags TYPE jsonb
  USING COALESCE(tags, '{}'::text[])::jsonb;

ALTER TABLE public.words
  ALTER COLUMN tags SET DEFAULT '[]'::jsonb;
```
### RSL
CREATE POLICY "admin full access words" ON public.words
  AS PERMISSIVE
  USING ((EXISTS ( SELECT 1
   FROM profiles
  WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "author insert own words" ON public.words
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = author_id));
CREATE POLICY "author read own words" ON public.words
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = author_id));
CREATE POLICY "author update own words" ON public.words
  AS PERMISSIVE FOR UPDATE
  USING ((auth.uid() = author_id));
CREATE POLICY "public read published words" ON public.words
  AS PERMISSIVE FOR SELECT
  USING ((status = 'published'::word_status));

## word_events
### sql
```sql
create table public.word_events (
  id uuid not null default gen_random_uuid (),
  word_id uuid not null,
  event_type public.word_event_type not null,
  actor_type text not null,
  actor_id uuid null,
  payload jsonb null,
  created_at timestamp with time zone null default now(),
  constraint word_events_pkey primary key (id),
  constraint word_events_word_id_fkey foreign KEY (word_id) references words (word_id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "admin full access word events" ON public.word_events
  AS PERMISSIVE
  USING ((EXISTS ( SELECT 1
   FROM profiles
  WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "insert word events" ON public.word_events
  AS PERMISSIVE FOR INSERT
  WITH CHECK (((actor_id = auth.uid()) OR (actor_type = ANY (ARRAY['ai'::text, 'system'::text]))));
CREATE POLICY "read related word events" ON public.word_events
  AS PERMISSIVE FOR SELECT
  USING ((EXISTS ( SELECT 1
   FROM words
  WHERE ((words.word_id = word_events.word_id) AND ((words.author_id = auth.uid()) OR (EXISTS ( SELECT 1
           FROM profiles
          WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))))))));

## user_personas
### sql
```sql
create table public.user_personas (
  id uuid not null,
  bio_summary text null,
  behavioral_tags text[] null default '{}'::text[],
  stats jsonb null default '{"tags": {}, "clicks": {}, "dwell_time": {}}'::jsonb,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  constraint user_personas_pkey primary key (id),
  constraint user_personas_id_fkey foreign KEY (id) references auth.users (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_user_personas_stats on public.user_personas using gin (stats) TABLESPACE pg_default;

create trigger update_user_personas_modtime BEFORE
update on user_personas for EACH row
execute FUNCTION update_updated_at_column ();
```
### RSL
CREATE POLICY "Users can view own persona" ON public.user_personas
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = id));

## treeholes
### sql
```sql
create table public.treeholes (
    id uuid not null default gen_random_uuid (),
    author_id uuid null,
    content text not null,
    is_anonymous boolean not null default true,
    mood text not null default '平常'::text,
    created_at timestamp with time zone null default now(),
  constraint treeholes_pkey primary key (id),
  constraint treeholes_author_id_fkey foreign KEY (author_id) references profiles (id) on delete set null
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "author insert" ON public.treeholes
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = author_id));
CREATE POLICY "author update" ON public.treeholes
  AS PERMISSIVE FOR UPDATE
  USING ((auth.uid() = author_id));
CREATE POLICY "public read" ON public.treeholes
  AS PERMISSIVE FOR SELECT
  USING (true);
## treehole_ai_replies
### sql
```sql
create table public.treehole_ai_replies (
  id uuid not null default gen_random_uuid (),
  treehole_id uuid not null,
  content text not null,
  created_at timestamp with time zone null default now(),
  constraint treehole_ai_replies_pkey primary key (id),
  constraint treehole_ai_replies_treehole_id_fkey foreign KEY (treehole_id) references treeholes (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "public read" ON public.treehole_ai_replies
  AS PERMISSIVE FOR SELECT
  USING (true);
CREATE POLICY "service insert" ON public.treehole_ai_replies
  AS PERMISSIVE FOR INSERT
  WITH CHECK (true);

## reports
### sql
```sql
create table public.reports (
  id uuid not null default gen_random_uuid (),
  reporter_id uuid null,
  target_type text not null,
  target_id uuid not null,
  reason text not null,
  created_at timestamp with time zone null default now(),
  constraint reports_pkey primary key (id),
  constraint reports_reporter_id_fkey foreign KEY (reporter_id) references profiles (id)
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "admin read" ON public.reports
  AS PERMISSIVE FOR SELECT
  USING ((EXISTS ( SELECT 1
   FROM profiles
  WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "user insert" ON public.reports
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = reporter_id));
## rag_summaries
### sql
```sql
create table public.rag_summaries (
  id uuid not null default gen_random_uuid (),
  user_id uuid null,
  query text not null,
  query_hash text not null,
  summary text not null,
  source_post_ids uuid[] not null,
  created_at timestamp with time zone null default now(),
  query_embedding public.vector null,
  constraint rag_summaries_pkey primary key (id),
  constraint rag_summaries_user_id_query_hash_key unique (user_id, query_hash)
) TABLESPACE pg_default;

create index IF not exists idx_rag_summaries_created_at on public.rag_summaries using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists rag_summaries_query_embedding_idx on public.rag_summaries using ivfflat (query_embedding vector_cosine_ops)
with
  (lists = '100') TABLESPACE pg_default;
```
### RSL
CREATE POLICY "no delete rag summaries" ON public.rag_summaries
  AS PERMISSIVE FOR DELETE
  USING (false);
CREATE POLICY "no update rag summaries" ON public.rag_summaries
  AS PERMISSIVE FOR UPDATE
  USING (false);
CREATE POLICY "read public or own rag summaries" ON public.rag_summaries
  AS PERMISSIVE FOR SELECT
  USING (((user_id IS NULL) OR (user_id = auth.uid())));
CREATE POLICY "service role insert rag summaries" ON public.rag_summaries
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.role() = 'service_role'::text));

## profiles
### sql
```sql
create table public.profiles (
  id uuid not null,
  username text not null,
  avatar_url text null,
  bio text null,
  role text not null default 'user'::text,
  created_at timestamp with time zone null default now(),
  profile_account text null,
  constraint profiles_pkey primary key (id),
  constraint profiles_username_key unique (username),
  constraint profiles_id_fkey foreign KEY (id) references auth.users (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "read own profile" ON public.profiles
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = id));
CREATE POLICY "update own profile" ON public.profiles
  AS PERMISSIVE FOR UPDATE
  USING ((auth.uid() = id));

## likes
### sql
```sql
create table public.likes (
  user_id uuid not null,
  post_id uuid not null,
  created_at timestamp with time zone null default now(),
  constraint likes_pkey primary key (user_id, post_id),
  constraint likes_user_id_fkey foreign KEY (user_id) references profiles (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "read all" ON public.likes
  AS PERMISSIVE FOR SELECT
  USING (true);
CREATE POLICY "user delete" ON public.likes
  AS PERMISSIVE FOR DELETE
  USING ((auth.uid() = user_id));
CREATE POLICY "user insert" ON public.likes
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = user_id));
## bookmarks
### sql
```sql
create table public.bookmarks (
  user_id uuid not null,
  post_id uuid not null,
  created_at timestamp with time zone null default now(),
  constraint bookmarks_pkey primary key (user_id, post_id),
  constraint bookmarks_user_id_fkey foreign KEY (user_id) references profiles (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "read own" ON public.bookmarks
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = user_id));
CREATE POLICY "user delete" ON public.bookmarks
  AS PERMISSIVE FOR DELETE
  USING ((auth.uid() = user_id));
CREATE POLICY "user insert" ON public.bookmarks
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = user_id));
## follows
### sql
```sql
create table public.follows (
  user_id uuid not null,
  follow_id uuid not null,
  created_at timestamp with time zone null default now(),
  constraint follows_pkey primary key (user_id, follow_id),
  constraint follows_user_id_fkey foreign KEY (user_id) references profiles (id) on delete CASCADE,
  constraint follows_follow_id_fkey foreign KEY (follow_id) references profiles (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "read own follows" ON public.follows
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = user_id));
CREATE POLICY "user delete follows" ON public.follows
  AS PERMISSIVE FOR DELETE
  USING ((auth.uid() = user_id));
CREATE POLICY "user insert follows" ON public.follows
  AS PERMISSIVE FOR INSERT
  WITH CHECK ((auth.uid() = user_id));
## notifications
### sql
```sql
create table public.notifications (
  id uuid not null default gen_random_uuid (),
  user_id uuid not null,
  type text not null,
  content text not null,
  ref_type text null,
  ref_id uuid null,
  is_read boolean not null default false,
  created_at timestamp with time zone null default now(),
  constraint notifications_pkey primary key (id),
  constraint notifications_user_id_fkey foreign KEY (user_id) references profiles (id) on delete CASCADE
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "read own notifications" ON public.notifications
  AS PERMISSIVE FOR SELECT
  USING ((auth.uid() = user_id));
CREATE POLICY "update own notifications" ON public.notifications
  AS PERMISSIVE FOR UPDATE
  USING ((auth.uid() = user_id));
CREATE POLICY "service insert notifications" ON public.notifications
  AS PERMISSIVE FOR INSERT
  WITH CHECK (true);
## ai_post_reviews
### sql
```sql
create table public.ai_post_reviews (
  id uuid not null default gen_random_uuid (),
  post_id uuid not null,
  result text not null,
  reason text null,
  created_at timestamp with time zone null default now(),
  constraint ai_post_reviews_pkey primary key (id)
) TABLESPACE pg_default;
```
### RSL
CREATE POLICY "admin read" ON public.ai_post_reviews
  AS PERMISSIVE FOR SELECT
  USING ((EXISTS ( SELECT 1
   FROM profiles
  WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "service insert" ON public.ai_post_reviews
  AS PERMISSIVE FOR INSERT
  WITH CHECK (true);

## change_version & change_log
### sql
```sql
create table public.change_version (
  id int primary key default 1,
  version bigint not null
);

insert into public.change_version (id, version)
values (1, 0)
on conflict (id) do nothing;

create table public.change_log (
  id bigserial primary key,
  entity_type text not null,
  entity_id uuid not null,
  change_type text not null,
  version bigint not null,
  changed_at timestamp with time zone not null default now()
);

create index idx_change_log_version on public.change_log (version);
create index idx_change_log_entity on public.change_log (entity_type, entity_id);
```
### functions & triggers
```sql
create or replace function next_change_version()
returns bigint language plpgsql as $$
declare v bigint;
begin
  update change_version set version = version + 1 where id = 1 returning version into v;
  return v;
end $$;

create or replace function log_change_words()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('words', coalesce(new.word_id, old.word_id), TG_OP, v);
  return coalesce(new, old);
end $$;

create or replace function log_change_comments()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('comments', coalesce(new.id, old.id), TG_OP, v);
  return coalesce(new, old);
end $$;

create or replace function log_change_likes()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('likes', coalesce(new.post_id, old.post_id), TG_OP, v);
  return coalesce(new, old);
end $$;

create or replace function log_change_bookmarks()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('bookmarks', coalesce(new.post_id, old.post_id), TG_OP, v);
  return coalesce(new, old);
end $$;

create or replace function log_change_notifications()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('notifications', coalesce(new.id, old.id), TG_OP, v);
  return coalesce(new, old);
end $$;

create or replace function log_change_treeholes()
returns trigger language plpgsql as $$
declare v bigint;
begin
  v := next_change_version();
  insert into change_log(entity_type, entity_id, change_type, version)
  values ('treeholes', coalesce(new.id, old.id), TG_OP, v);
  return coalesce(new, old);
end $$;

create trigger trg_words_change
after insert or update or delete on public.words
for each row execute function log_change_words();

create trigger trg_comments_change
after insert or update or delete on public.comments
for each row execute function log_change_comments();

create trigger trg_likes_change
after insert or update or delete on public.likes
for each row execute function log_change_likes();

create trigger trg_bookmarks_change
after insert or update or delete on public.bookmarks
for each row execute function log_change_bookmarks();

create trigger trg_notifications_change
after insert or update or delete on public.notifications
for each row execute function log_change_notifications();

create trigger trg_treeholes_change
after insert or update or delete on public.treeholes
for each row execute function log_change_treeholes();
```
### RSL
```sql
CREATE POLICY "admin read change_log" ON public.change_log
  AS PERMISSIVE FOR SELECT
  USING ((EXISTS ( SELECT 1 FROM profiles WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "service insert change_log" ON public.change_log
  AS PERMISSIVE FOR INSERT
  WITH CHECK (true);
CREATE POLICY "admin read change_version" ON public.change_version
  AS PERMISSIVE FOR SELECT
  USING ((EXISTS ( SELECT 1 FROM profiles WHERE ((profiles.id = auth.uid()) AND (profiles.role = 'admin'::text)))));
CREATE POLICY "service update change_version" ON public.change_version
  AS PERMISSIVE FOR UPDATE
  USING (true);
```
