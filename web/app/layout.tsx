import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Short Form",
  description: "Turn any Shopify product URL into a UGC video ad in minutes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white min-h-screen">{children}</body>
    </html>
  );
}
