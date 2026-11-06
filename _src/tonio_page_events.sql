-- Table de suivi des visiteurs des landing pages Tonio Rénov'.
-- À exécuter UNE FOIS dans l'éditeur SQL du nouveau CRM Potentieel OS
-- (projet Supabase ktzegmikprmltuelxsgi).

create table if not exists public.tonio_page_events (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  event_type  text not null,              -- pageview, scroll_10..100, engaged_15s.., click_call, click_cta_devis, form_in_view, form_start, form_step_1..4, form_submit_success, page_exit
  page        text not null,              -- pathname (/peinture-interieure, /couvreur, …)
  session_id  text not null,              -- un onglet = une session
  user_agent  text,
  referrer    text,
  meta        jsonb not null default '{}'::jsonb  -- utm_*, gclid, zone, pos, time_on_page_s, max_scroll, etc.
);

-- Index utiles pour le futur tableau de bord CRM
create index if not exists tonio_page_events_created_at_idx on public.tonio_page_events (created_at desc);
create index if not exists tonio_page_events_page_idx       on public.tonio_page_events (page, created_at desc);
create index if not exists tonio_page_events_session_idx    on public.tonio_page_events (session_id, created_at);
create index if not exists tonio_page_events_event_idx      on public.tonio_page_events (event_type, created_at desc);
create index if not exists tonio_page_events_gclid_idx      on public.tonio_page_events ((meta->>'gclid')) where meta ? 'gclid';

-- RLS : les landings écrivent avec la clé anon, seul l'admin lit.
alter table public.tonio_page_events enable row level security;

drop policy if exists tonio_page_events_insert_anon  on public.tonio_page_events;
drop policy if exists tonio_page_events_select_admin on public.tonio_page_events;

create policy tonio_page_events_insert_anon
  on public.tonio_page_events for insert
  to anon, authenticated
  with check (true);

-- À adapter avec l'email réel de l'admin du nouveau CRM (ou le claim is_admin)
create policy tonio_page_events_select_admin
  on public.tonio_page_events for select
  to authenticated
  using (
    (auth.jwt() ->> 'email') in (
      'emrick.perilliat2006@gmail.com',
      'contact@potentieel.fr'
    )
  );

-- --------- Vue d'agrégat par page (5 derniers jours) ---------
-- Utile côté CRM : combien de visiteurs, scroll moyen, taux de conversion,
-- combien ont cliqué sur le téléphone, démarré/soumis le formulaire.
create or replace view public.v_tonio_lp_stats as
with sessions as (
  select
    session_id,
    page,
    min(created_at)                                    as debut,
    max(created_at)                                    as fin,
    bool_or(event_type = 'click_call')                 as a_clique_tel,
    bool_or(event_type = 'click_cta_devis')            as a_clique_devis,
    bool_or(event_type = 'form_in_view')               as form_vu,
    bool_or(event_type = 'form_start')                 as form_demarre,
    bool_or(event_type = 'form_submit_success')        as form_soumis,
    bool_or(event_type = 'engaged_30s')                as engage_30s,
    max(case
      when event_type ~ '^scroll_[0-9]+$'
      then (regexp_replace(event_type, '^scroll_', ''))::int end) as scroll_max,
    max((meta->>'time_on_page_s')::int)                as temps_total_s
  from public.tonio_page_events
  where created_at > now() - interval '30 days'
  group by session_id, page
)
select
  page,
  date_trunc('day', debut)                             as jour,
  count(*)                                             as visites,
  sum(case when engage_30s then 1 else 0 end)          as visiteurs_engages,
  round(avg(scroll_max)::numeric, 1)                   as scroll_moyen,
  round(avg(temps_total_s)::numeric, 1)                as temps_moyen_s,
  sum(case when a_clique_tel then 1 else 0 end)        as clics_tel,
  sum(case when a_clique_devis then 1 else 0 end)      as clics_devis,
  sum(case when form_vu then 1 else 0 end)             as form_vus,
  sum(case when form_demarre then 1 else 0 end)        as form_demarres,
  sum(case when form_soumis then 1 else 0 end)         as form_soumis,
  round(100.0 * sum(case when form_soumis then 1 else 0 end) / nullif(count(*),0), 2) as taux_conv_pct
from sessions
group by page, jour
order by jour desc, page;
