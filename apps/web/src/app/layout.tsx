// apps/web/src/app/layout.tsx
import type { Metadata } from "next";
import dynamic from "next/dynamic";
import { Inter } from "next/font/google";

import "@/styles/globals.css";
import ProvidersWrapper from "@/app/(providers)/ProvidersWrapper";


// Dynamically import Nav component with ssr: false
const Nav = dynamic(() => import("@/app/(providers)/Nav"), { ssr: false });

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FiCast Next App",
  description: "FiCast is a content delivery system that augments our ideation & learning with thoughtful conversations between agentic models that LLM imagines them to be.",
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className} style={{ backgroundColor: 'inherit' }}>
      <body>
        <ProvidersWrapper>
          <Nav />
          {children}
        </ProvidersWrapper>
      </body>
    </html>
  );
}