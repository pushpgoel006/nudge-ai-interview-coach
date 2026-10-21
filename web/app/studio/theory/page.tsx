import { RequireSession } from "@/components/studio/RequireSession";
import { TheorySection } from "@/components/studio/TheorySection";

export default function TheoryPage() {
  return (
    <RequireSession>
      <TheorySection />
    </RequireSession>
  );
}
