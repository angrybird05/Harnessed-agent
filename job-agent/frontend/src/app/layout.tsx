import type { Metadata } from "next";
import "./globals.css";
import NavClient from "@/components/NavClient";

export const metadata: Metadata = {
  title: "JobBot AI - Autonomous Job Application System",
  description:
    "AI-powered system that autonomously discovers, applies to, and follows up on job applications.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-surface-900 text-white font-sans antialiased min-h-screen">
        <NavClient />
        <main className="pt-20 pb-12 px-6 max-w-7xl mx-auto">{children}</main>
      </body>
    </html>
  );
}
