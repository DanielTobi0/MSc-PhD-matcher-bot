-- Security hardening (review 2): B6, B7, B8, B13.

-- B6. Server-side bounds on user-written text and numbers.
alter table public.user_notes
  add constraint user_notes_note_len check (char_length(note) <= 5000) not valid;
alter table public.user_profiles
  add constraint user_profiles_threshold_range check (min_score_threshold between 0 and 100) not valid;

-- B8. is_personalised only answers for the caller; it no longer reveals other users' state.
create or replace function public.is_personalised(uid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select uid = auth.uid()
     and exists (select 1 from user_llm_keys k where k.user_id = uid)
     and exists (select 1 from user_cv c where c.user_id = uid and (c.parse_status = 'done' or c.parsed <> '{}'::jsonb))
     and exists (select 1 from user_profiles p where p.id = uid and p.onboarding_step >= 5);
$$;

-- B13. Users may read and update their profile, not delete it (the signup trigger is the only creator).
drop policy if exists "users manage own profile" on public.user_profiles;
create policy "users read own profile" on public.user_profiles
  for select to authenticated using (auth.uid() = id);
create policy "users update own profile" on public.user_profiles
  for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);
revoke delete on public.user_profiles from authenticated, anon;

-- B7. Serialise the rate-limit check per (function, user) so parallel requests cannot all pass.
create or replace function public.rate_limit_hit(p_user_id uuid, p_fn text, p_max int, p_window interval)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare recent int;
begin
  perform pg_advisory_xact_lock(hashtext(p_fn || ':' || coalesce(p_user_id::text, 'global')));
  delete from rate_limit_events where created_at < now() - interval '2 days' and fn = p_fn;
  select count(*) into recent from rate_limit_events
   where fn = p_fn and created_at > now() - p_window
     and (p_user_id is null or user_id = p_user_id);
  if recent >= p_max then
    return false;
  end if;
  insert into rate_limit_events (user_id, fn)
  values (coalesce(p_user_id, '00000000-0000-0000-0000-000000000000'), p_fn);
  return true;
end;
$$;
