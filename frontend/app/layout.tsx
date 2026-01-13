import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SOFWeek Speaker Recommendations",
  description: "AI-powered speaker matching for SOFWeek 2025",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
