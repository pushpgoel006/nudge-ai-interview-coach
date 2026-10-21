import { RequireSession } from "@/components/studio/RequireSession";
import { ResumeSection } from "@/components/studio/ResumeSection";

export default function ResumePage() {
  return (
    <RequireSession>
      <ResumeSection />
    </RequireSession>
  );
}
