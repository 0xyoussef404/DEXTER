import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BugHunterX - Security Platform",
  description: "Advanced security testing platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="light-scheme">
      <body>{children}</body>
    </html>
  );
}
