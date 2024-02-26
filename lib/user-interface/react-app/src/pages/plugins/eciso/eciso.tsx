import { useState } from "react";
import BaseAppLayout from "../../../components/base-app-layout";
import EcisoChat from "../../../components/plugins/eciso/eciso-chat";
import EcisoSessions from "../../../components/plugins/eciso/eciso-sessions";
import { useParams } from "react-router-dom";

export default function Eciso() {
  const { sessionId } = useParams();
  const [toolsOpen, setToolsOpen] = useState(false);

  return (
    <BaseAppLayout
      toolsHide={false}
      toolsOpen={toolsOpen}
      onToolsChange={({ detail }) => setToolsOpen(detail.open)}
      tools={<EcisoSessions toolsOpen={toolsOpen} />}
      toolsWidth={500}
      content={<EcisoChat sessionId={sessionId} />}
    />
  );
}
