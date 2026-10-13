import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// next/font downloads and self-hosts Inter at build/dev time (needs internet once). Tamil and
// Devanagari fall back to Noto / Nirmala UI through the CSS font stack.
const inter = Inter({ variable: "--font-inter", subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "FloodPath-Care",
  description:
    "Flood-aware emergency routing to maternal facilities: a historical-data-informed simulation of Chennai 2015.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
