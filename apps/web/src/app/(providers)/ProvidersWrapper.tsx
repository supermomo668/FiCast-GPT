"use client";
import { SessionProvider } from "next-auth/react";
import { NextUIProvider } from "@nextui-org/react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import "@/styles/globals.css";

export default function ProvidersWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionProvider>
      {/* <NextThemesProvider defaultTheme="system" attribute="class"> */}
        {/* <NextUIProvider>{children}</NextUIProvider> */}
        {children}
      {/* </NextThemesProvider> */}
    </SessionProvider>
  );
}

// export default function ProvidersWrapper({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <SessionProvider>
//       <NextThemesProvider defaultTheme="system" attribute="class">
//         <NextUIProvider>{children}</NextUIProvider>
//       </NextThemesProvider>
//     </SessionProvider>
//   );
// }
