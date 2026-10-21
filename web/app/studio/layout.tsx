import type { Metadata } from "next";
import type { ReactNode } from "react";
import { StudioProvider } from "@/components/studio/StudioProvider";

export const metadata: Metadata = {
  title: "Studio | Nudge",
  description: "Practise with your own JD and resume.",
  robots: { index: false },
};

export default function StudioLayout({ children }: { children: ReactNode }) {
  return <StudioProvider>{children}</StudioProvider>;
}
