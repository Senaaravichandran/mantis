"use client";

import "./globals.css";
import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { staleTime: 30000, refetchInterval: 60000 },
    },
  }));

  return (
    <html lang="en">
      <head>
        <title>MANTIS - Infrastructure Intelligence Platform</title>
        <meta name="description" content="Mantis Infrastructure Intelligence Platform" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
              <Header />
              <main className="flex-1 overflow-auto bg-gray-50 p-6">
                {children}
              </main>
            </div>
          </div>
        </QueryClientProvider>
      </body>
    </html>
  );
}
