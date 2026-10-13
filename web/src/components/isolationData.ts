// Isolation data types and helpers with no map code, so the Export page can import them during
// server rendering (react-leaflet needs `window`). Data comes from isolation.json
// (scripts/build_isolation.py).
import { useEffect, useState } from "react";
import type { GeoJsonObject } from "geojson";
import { getJson, toCsv } from "@/lib/download";

export type IsoUnit = {
  unit_id: string; unit_name: string; population: number; population_basis: string; nodes_total: number;
  nodes_eligible: number; nodes_baseline_disconnected: number; nodes_isolated: number; nodes_delayed: number;
  isolated_share: number; delayed_share: number; estimated_people_isolated: number; priority_score: number; rank: number;
};
export type IsoFile = {
  grid_m: number; top_k: number; population_basis: string;
  scenarios: Record<string, { units: IsoUnit[]; warnings: string[]; nodes_baseline_disconnected: number; units_with_isolation: number }>;
  cells: GeoJsonObject;
};
export const SIM = ["mild", "moderate", "severe"] as const;
const CSV_COLUMNS = ["ui_language", "scenario", "rank", "unit_id", "population", "population_basis", "nodes_eligible",
  "nodes_baseline_disconnected", "nodes_isolated", "nodes_delayed", "isolated_share", "delayed_share",
  "estimated_people_isolated", "priority_score"];

export function useIsolation() {
  const [data, setData] = useState<IsoFile | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    getJson<IsoFile>("/data/isolation.json").then(setData).catch(() => setFailed(true));
  }, []);
  return { data, failed };
}

export function isolationCsv(data: IsoFile, lang: string, scenarios: readonly string[] = ["observed", ...SIM]): string {
  const rows = scenarios.flatMap((s) => data.scenarios[s].units.map((u) => ({ ui_language: lang, scenario: s, ...u })));
  return toCsv(CSV_COLUMNS, rows);
}

