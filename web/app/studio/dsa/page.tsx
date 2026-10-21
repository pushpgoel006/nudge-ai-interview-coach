import { RequireSession } from "@/components/studio/RequireSession";
import { DsaSection } from "@/components/studio/DsaSection";

export default function DsaPage() {
  return (
    <RequireSession>
      <DsaSection />
    </RequireSession>
  );
}
