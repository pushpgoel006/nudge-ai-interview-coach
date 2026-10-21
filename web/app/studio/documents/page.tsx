import { RequireSession } from "@/components/studio/RequireSession";
import { DocumentsSection } from "@/components/studio/DocumentsSection";

export default function DocumentsPage() {
  return (
    <RequireSession>
      <DocumentsSection />
    </RequireSession>
  );
}
