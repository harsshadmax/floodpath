// Translation helpers (blueprint Section 4.12, 6A). The dictionaries are copied from the project's
// i18n/*.json by scripts/export_web_i18n.py, so Python and Next.js share one source of truth.
// Tamil and Hindi strings are DRAFT translations until reviewed (docs/TRANSLATION_REVIEW.md).
import en from "@/i18n/en.json";
import ta from "@/i18n/ta.json";
import hi from "@/i18n/hi.json";

export type Lang = "en" | "ta" | "hi";
export const LANGS: Lang[] = ["en", "ta", "hi"];
export const DEFAULT_LANG: Lang = "en";
// Each language is shown in its own script (blueprint I18N-5).
export const LANG_LABELS: Record<Lang, string> = { en: "English", ta: "தமிழ்", hi: "हिन्दी" };

type Dict = Record<string, unknown>;
const DICTS: Record<Lang, Dict> = { en: en as Dict, ta: ta as Dict, hi: hi as Dict };

export function normalizeLang(value: string | null | undefined): Lang {
  return value && (LANGS as string[]).includes(value) ? (value as Lang) : DEFAULT_LANG;
}

function lookup(lang: Lang, key: string): string | undefined {
  const value = DICTS[lang][key];
  return typeof value === "string" ? value : undefined;
}

/** Translate `key`. Falls back to English, then to the key itself, and reports the fallback. */
export function t(lang: Lang, key: string, params: Record<string, string | number> = {}): string {
  let text = lookup(lang, key);
  if (text === undefined) {
    console.warn(`I18N_KEY_MISSING: ${key} missing in ${lang}`);
    text = lookup(DEFAULT_LANG, key);
    if (text === undefined) {
      console.warn(`I18N_KEY_MISSING: ${key} missing in English`);
      return key;
    }
  }
  return text.replace(/\{(\w+)\}/g, (match, name: string) => {
    if (name in params) return String(params[name]);
    console.error(`I18N_PARAM_MISSING: ${key} needs {${name}}`);
    return match;
  });
}

/** Indian digit grouping with Western digits (assumption A-18): 1234567 -> 12,34,567. */
export function fmtInt(n: number): string {
  const value = Math.round(n);
  const sign = value < 0 ? "-" : "";
  const digits = String(Math.abs(value));
  if (digits.length <= 3) return sign + digits;
  let head = digits.slice(0, -3);
  const tail = digits.slice(-3);
  const groups: string[] = [];
  while (head.length > 0) {
    groups.unshift(head.slice(-2));
    head = head.slice(0, -2);
  }
  return sign + [...groups, tail].join(",");
}

/** A fraction as NN.N%: 0.1234 -> 12.3%. */
export function fmtPct(x: number): string {
  return `${(x * 100).toFixed(1)}%`;
}

/** Translation status ('draft' or 'reviewed') from the dictionary's _meta block. */
export function translationStatus(lang: Lang): "draft" | "reviewed" {
  const meta = DICTS[lang]["_meta"] as { status?: string } | undefined;
  return meta?.status === "reviewed" ? "reviewed" : "draft";
}

export function englishOriginal(key: string): string {
  return lookup("en", key) ?? key;
}
