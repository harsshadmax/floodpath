"use client";
// PHASE 1 preview skeleton in the final layout. Overview and Route show translated "Not built yet"
// placeholders; Data and limits is already real. No analysis result is shown anywhere yet.
import { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import config from "@/data/config.json";
import { LANGS, LANG_LABELS, englishOriginal, normalizeLang, t, translationStatus, type Lang } from "@/lib/i18n";
import { DashboardIcon, InfoIcon, RouteIcon } from "./icons";
import { Banner, Card, DatePill, KpiCard, Notice, Pills, Placeholder, Rail, type RailItem } from "./ui";

type PageId = "overview" | "route" | "data";
const SCENARIOS = ["observed", "mild", "moderate", "severe"] as const;
type Scenario = (typeof SCENARIOS)[number];
const FOCUS = ["reachability", "coverage", "time"] as const;
type Focus = (typeof FOCUS)[number];
const KPI_KEYS = ["kpi.time_increase", "kpi.feasibility", "kpi.reachability", "kpi.coverage", "kpi.robustness"];
const GAP_KEYS = ["gap.facility_list", "gap.ambulance", "gap.peak", "gap.roads"];

export default function Dashboard() {
  const [page, setPage] = useState<PageId>("overview");
  const [scenario, setScenario] = useState<Scenario>("observed");
  const [focus, setFocus] = useState<Focus>("reachability");

  // The language lives in the page address (?lang=ta), so a shared link opens in that language
  // (blueprint I18N-5) and an unsupported value falls back to English.
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const lang: Lang = normalizeLang(searchParams.get("lang"));

  useEffect(() => {
    document.documentElement.lang = lang; // lets the CSS switch off letter-spacing for ta and hi
  }, [lang]);

  const changeLang = (next: Lang) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("lang", next);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  const T = (key: string, params?: Record<string, string | number>) => t(lang, key, params);
  const kind = scenario === "observed" ? T("badge.composite") : T("badge.simulated");
  const caption = `${T("scenario." + scenario)}  |  ${kind}`;

  // Two icon groups divided by a thin line, like the reference rail; Data and limits takes the info slot.
  const navGroups: RailItem[][] = [
    [
      { id: "overview", label: T("nav.overview"), icon: <DashboardIcon /> },
      { id: "route", label: T("nav.route"), icon: <RouteIcon /> },
    ],
    [{ id: "data", label: T("nav.data"), icon: <InfoIcon /> }],
  ];

  return (
    <div className="fp-shell">
      <Rail groups={navGroups} active={page} onSelect={(id) => setPage(id as PageId)} />
      <main className="fp-main">
        <header className="fp-header">
          <div className="fp-header-left">
            <h1 className="fp-title">{T("app.title")}</h1>
            <p className="fp-subtitle">{T("app.subtitle")}</p>
          </div>
          <div className="fp-header-right">
            <div className="fp-row fp-row-right">
              <Pills
                variant="light"
                label={T("nav.language")}
                value={lang}
                onChange={changeLang}
                options={LANGS.map((l) => ({ value: l, label: LANG_LABELS[l] }))}
              />
              <DatePill text={T("event.chennai_2015")} />
            </div>
            <Pills
              variant="dark"
              label="focus"
              value={focus}
              onChange={setFocus}
              options={FOCUS.map((f) => ({ value: f, label: T("focus." + f) }))}
            />
          </div>
        </header>

        {/* Scenario control: its own full-width row so long Tamil and Hindi labels wrap, never truncate (A-19) */}
        <div className="fp-scenario-row">
          <Pills
            variant="light"
            label={T("label.scenario")}
            value={scenario}
            onChange={setScenario}
            options={SCENARIOS.map((s) => ({ value: s, label: T("scenario." + s) }))}
          />
        </div>

        <Banner text={T("banner.simulation")} />

        {page === "overview" && (
          <>
            <Notice text={T("app.skeleton_notice")} />
            <div className="fp-grid-kpi">
              {KPI_KEYS.map((key) => (
                <KpiCard key={key} label={T(key)} value={null} notBuilt={T("state.not_built")} />
              ))}
            </div>
            <div className="fp-grid-cards">
              {["card.map", "card.coverage_by_scenario", "card.isolation_top", "card.edge_classes", "card.reach_by_facility", "card.top_origins"].map(
                (key) => (
                  <Card key={key} title={T(key)} caption={caption}>
                    <Placeholder text={T("state.not_built")} />
                  </Card>
                ),
              )}
            </div>
          </>
        )}

        {page === "route" && (
          <Card title={T("page.route.title")} caption={caption}>
            <Placeholder text={T("state.not_built")} />
          </Card>
        )}

        {page === "data" && <DataPage lang={lang} />}
      </main>
    </div>
  );
}

function DataPage({ lang }: { lang: Lang }) {
  const T = (key: string) => t(lang, key);
  return (
    <div>
      <h2 className="fp-h2">{T("page.data.gaps_title")}</h2>
      <div className="fp-stack">
        {GAP_KEYS.map((key) => (
          <div className="fp-card" key={key}>
            <div>{T(key)}</div>
            {lang !== "en" && (
              // "Original English" line so a reader can check the meaning (blueprint 6.9)
              <p className="fp-original">
                {T("page.data.original_english")}: {englishOriginal(key)}
              </p>
            )}
          </div>
        ))}
      </div>

      <h2 className="fp-h2">{T("page.data.datasets_title")}</h2>
      <div className="fp-card">
        <table className="fp-table">
          <thead>
            <tr>
              <th>{T("table.dataset")}</th>
              <th>{T("table.type")}</th>
              <th>{T("table.licence")}</th>
            </tr>
          </thead>
          <tbody>
            {config.datasets.map((d) => (
              <tr key={d.id}>
                <td>
                  <span className="fp-mono">{d.id}</span> {d.name}
                </td>
                <td>{d.typeKey ? <span className="fp-badge">{T(d.typeKey)}</span> : "-"}</td>
                <td>{d.licence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="fp-h2">{T("page.data.assumptions_title")}</h2>
      <div className="fp-card">
        <table className="fp-table">
          <thead>
            <tr>
              <th>{T("table.parameter")}</th>
              <th>{T("table.value")}</th>
            </tr>
          </thead>
          <tbody>
            {config.assumptions.map((a) => (
              <tr key={a.name}>
                <td className="fp-mono">{a.name}</td>
                <td>{typeof a.value === "object" ? JSON.stringify(a.value) : String(a.value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="fp-h2">{T("page.data.translation_status")}</h2>
      <div className="fp-card">
        {LANGS.map((l) => (
          <div key={l}>
            <strong>{LANG_LABELS[l]}</strong>: {T(translationStatus(l) === "reviewed" ? "status.reviewed" : "status.draft")}
          </div>
        ))}
      </div>
    </div>
  );
}
