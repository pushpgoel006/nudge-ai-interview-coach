import { RequireSession } from "@/components/studio/RequireSession";
import { ChatSection } from "@/components/studio/ChatSection";

export default function ChatPage() {
  return (
    <RequireSession>
      <ChatSection />
    </RequireSession>
  );
}
