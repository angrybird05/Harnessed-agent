"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/applications", label: "Applications" },
  { href: "/profile", label: "Profile" },
];

const PUBLIC_PATHS = ["/login"];

export default function NavClient() {
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);

    // Redirect to login if not authenticated and not on a public page
    if (!token && !PUBLIC_PATHS.includes(pathname)) {
      window.location.href = "/login";
    }
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  };

  // Don't render nav on login page
  if (PUBLIC_PATHS.includes(pathname)) return null;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-surface-900/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-sm font-bold">
            JB
          </div>
          <span className="text-lg font-semibold bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
            JobBot AI
          </span>
        </a>
        <div className="flex items-center gap-1">
          {NAV_LINKS.map(({ href, label }) => (
            <a
              key={href}
              href={href}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                pathname === href
                  ? "text-white bg-white/10 border border-white/10"
                  : "text-surface-200 hover:text-white hover:bg-white/5"
              }`}
            >
              {label}
            </a>
          ))}
          {isLoggedIn && (
            <button
              onClick={handleLogout}
              className="ml-2 px-4 py-2 rounded-lg text-sm font-medium text-red-400/80 hover:text-red-400 hover:bg-red-500/5 transition-all duration-200"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
