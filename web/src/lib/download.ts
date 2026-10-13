// Browser-side file helpers for the Export page and the audit button. Files are built from the JSON
// the Python pipeline wrote to public/data/, never from invented values.

export async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return (await res.json()) as T;
}

export function saveFile(name: string, mime: string, text: string): void {
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

/** CSV with quoted fields where needed. Files use English column names (blueprint I18N-12). */
export function toCsv(columns: string[], rows: Record<string, unknown>[]): string {
  const cell = (v: unknown) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [columns.join(","), ...rows.map((r) => columns.map((c) => cell(r[c])).join(","))].join("\n") + "\n";
}

export async function downloadAudit(scenario: string, pointId: string, lang: string): Promise<void> {
  const all = await getJson<Record<string, Record<string, Record<string, unknown>>>>("/data/audit.json");
  const doc = { ...all[scenario][pointId], generated_at: new Date().toISOString(), ui_language: lang };
  saveFile(`floodpath_audit_${scenario}_${pointId}.json`, "application/json", JSON.stringify(doc, null, 2));
}
