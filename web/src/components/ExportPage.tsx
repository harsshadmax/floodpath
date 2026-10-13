"use client";
// Export page: CSV and JSON files built in the browser from the pipeline's JSON. English column names,
// with the interface language written into every file (blueprint I18N-12).
import { useEffect, useState } from "react";
import { t, type Lang } from "@/lib/i18n";
import { downloadAudit, getJson, saveFile, toCsv } from "@/lib/download";
import { isolationCsv, type IsoFile } from "./isolationData";
import { metricsCsv } from "./MetricsTable";
import type { MetricsFile } from "./Charts";

type Audit = Record<string, Record<string, { facilities: { used: Record<string, unknown>[]; excluded: { facility_id: string; reason: string }[] } }>>;

export default function ExportPage({ scenario, lang }: { scenario: string; lang: Lang }) {
  const T = (k: string) => t(lang, k);
  const [failed, setFailed] = useState(false);
  const [points, setPoints] = useState<string[]>([]);
  const [pointId, setPointId] = useState("A01");

  useEffect(() => {
    getJson<{ points: { id: string }[] }>("/data/routes.json").then((r) => setPoints(r.points.map((p) => p.id))).catch(() => undefined);
  }, []);

  const run = async (job: () => Promise<void>) => {
    try {
      await job();
      setFailed(false);
    } catch {
      setFailed(true);
    }
  };

  const facilitiesCsv = async () => {
    const audit = await getJson<Audit>("/data/audit.json");
    const { used, excluded } = audit.mild.A01.facilities;
    const cols = ["ui_language", "facility_id", "name", "latitude", "longitude", "service", "tier", "verification_status",
      "source", "verified_on", "snap_m", "routed", "excluded_reason", "notes"];
    const rows = [
      ...used.map((f) => ({ ui_language: lang, ...f, routed: "yes", excluded_reason: "" })),
      ...excluded.map((e) => ({ ui_language: lang, facility_id: e.facility_id, routed: "no", excluded_reason: e.reason })),
    ];
    saveFile("floodpath_facilities.csv", "text/csv", toCsv(cols, rows));
  };

  const items: { label: string; button: string; action: () => Promise<void> }[] = [
    { label: T("export.metrics_csv"), button: T("button.download_csv"), action: async () => saveFile("floodpath_metrics.csv", "text/csv", metricsCsv(await getJson<MetricsFile>("/data/metrics.json"), lang)) },
    { label: T("export.facilities_csv"), button: T("button.download_csv"), action: facilitiesCsv },
    { label: T("export.isolation_csv"), button: T("button.download_csv"), action: async () => saveFile("floodpath_isolation.csv", "text/csv", isolationCsv(await getJson<IsoFile>("/data/isolation.json"), lang)) },
    { label: T("export.audit_json"), button: T("button.download_audit"), action: () => downloadAudit(scenario, pointId, lang) },
  ];

  return (
    <div>
      <p className="fp-metrics-note">{T("export.intro")}</p>
      <ul className="fp-export-list">
        {items.map((it) => (
          <li key={it.label}>
            <span>{it.label}</span>
            <button type="button" className="fp-btn" onClick={() => run(it.action)}>{it.button}</button>
          </li>
        ))}
      </ul>
      <label className="fp-select-label" htmlFor="export-start">{T("route.pick_origin")}</label>
      <select id="export-start" className="fp-select fp-select-narrow" value={pointId} onChange={(e) => setPointId(e.target.value)}>
        {points.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      {failed && <p className="fp-muted">{T("export.failed")}</p>}
    </div>
  );
}
