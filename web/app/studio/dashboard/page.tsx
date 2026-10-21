import { RequireSession } from "@/components/studio/RequireSession";
import { DashboardSection } from "@/components/studio/DashboardSection";

export default function DashboardPage() {
  return (
    <RequireSession>
      <DashboardSection />
    </RequireSession>
  );
}
