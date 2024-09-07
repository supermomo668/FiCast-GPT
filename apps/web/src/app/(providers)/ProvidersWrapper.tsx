"use client";
import { NextUIProvider } from "@nextui-org/react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import "@/styles/globals.css";

export default function ProvidersWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // You can still use other providers like NextUIProvider or NextThemesProvider if needed
    <>
      <NextThemesProvider defaultTheme="system" attribute="class">
        <NextUIProvider>{children}</NextUIProvider>
      </NextThemesProvider>
    </>
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
