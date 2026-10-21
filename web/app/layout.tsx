import type { Metadata } from "next";
import { Inter_Tight } from "next/font/google";
import "./globals.css";

const inter = Inter_Tight({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nudge | AI interview coach",
  description: "Nudge is the AI interview coach that practises with your own JD and resume.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <noscript>
          <style>{".loader{display:none}body.is-loading{overflow:auto}"}</style>
        </noscript>
        {children}
      </body>
    </html>
  );
}
