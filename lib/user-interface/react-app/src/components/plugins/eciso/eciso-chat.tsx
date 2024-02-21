import { useContext, useEffect, useState } from "react";
import {
  ChatBotConfiguration,
  ChatBotHistoryItem,
  ChatBotMessageType,
  FeedbackData,
} from "../../chatbot/types";
import { SpaceBetween, StatusIndicator } from "@cloudscape-design/components";
import { v4 as uuidv4 } from "uuid";
import { AppContext } from "../../../common/app-context";
import { ApiClient } from "../../../common/api-client/api-client";
import ChatMessage from "../../chatbot/chat-message";
import EcisoChatInputPanel, { EcisoChatScrollState } from "./eciso-chat-input-panel";
import styles from "../../../styles/chat.module.scss";
import { PLUGIN_ECISO_CHATBOT_NAME,PLUGIN_ECISO_LOGO } from "../../../common/constants";

export default function EcisoChat(props: { sessionId?: string }) {
  const appContext = useContext(AppContext);
  const [running, setRunning] = useState<boolean>(false);
  const [session, setSession] = useState<{ id: string; loading: boolean }>({
    id: props.sessionId ?? uuidv4(),
    loading: typeof props.sessionId !== "undefined",
  });
  const [configuration, setConfiguration] = useState<ChatBotConfiguration>(
    () => ({
      streaming: false,
      showMetadata: false,
      maxTokens: 512,
      temperature: 0,
      topP: 0,
      files: null,
    })
  );

  const [messageHistory, setMessageHistory] = useState<ChatBotHistoryItem[]>(
    []
  );

  useEffect(() => {
    if (!appContext) return;
    setMessageHistory([]);

    (async () => {
      if (!props.sessionId) {
        setSession({ id: uuidv4(), loading: false });
        return;
      }

      setSession({ id: props.sessionId, loading: true });
      const apiClient = new ApiClient(appContext);
      try {
        const result = await apiClient.sessions.GetEcisoSessionQuery(props.sessionId);

        if (result.data?.getEcisoSession?.history) {
          console.log(result.data.getEcisoSession);
          EcisoChatScrollState.skipNextHistoryUpdate = true;
          EcisoChatScrollState.skipNextScrollEvent = true;
          console.log("History", result.data.getEcisoSession.history);
          setMessageHistory(
            result
              .data!.getEcisoSession!.history.filter((x) => x !== null)
              .map((x) => ({
                type: x!.type as ChatBotMessageType,
                metadata: JSON.parse(x!.metadata!),
                content: x!.content,
              }))
          );

          window.scrollTo({
            top: 0,
            behavior: "instant",
          });
        }
      } catch (error) {
        console.log(error);
      }

      setSession({ id: props.sessionId, loading: false });
      setRunning(false);
    })();
  }, [appContext, props.sessionId]);

  const handleFeedback = (feedbackType: 1 | 0, idx: number, message: ChatBotHistoryItem) => {
    if (message.metadata.sessionId) {
      const prompt = messageHistory[idx - 1]?.content;
      const completion = message.content;
      const model = message.metadata.modelId;
      const feedbackData: FeedbackData = {
        sessionId: message.metadata.sessionId as string,
        key: idx,
        feedback: feedbackType,
        prompt: prompt,
        completion: completion,
        model: model as string
      };
      addUserFeedback(feedbackData);
    }
  };

  const addUserFeedback = async (feedbackData: FeedbackData) => {
    if (!appContext) return;

    const apiClient = new ApiClient(appContext);
    await apiClient.userFeedback.addUserFeedback({feedbackData});
  };

  return (
    <div className={styles.chat_container}>
      <SpaceBetween direction="vertical" size="m">
        {messageHistory.map((message, idx) => (
          <ChatMessage
            key={idx}
            message={message}
            showMetadata={configuration.showMetadata}
            onThumbsUp={() => handleFeedback(1, idx, message)}
            onThumbsDown={() => handleFeedback(0, idx, message)}
          />
        ))}
      </SpaceBetween>
      <div className={styles.welcome_text}>
        {messageHistory.length == 0 && !session?.loading && (
          <center>
            {PLUGIN_ECISO_CHATBOT_NAME}
            <br/>
                <img src={PLUGIN_ECISO_LOGO} alt="Cal Poly" />
          </center>

        )}
        {session?.loading && (
          <center>
            <StatusIndicator type="loading">Loading session</StatusIndicator>
          </center>
        )}
      </div>
      <div className={styles.input_container}>
        <EcisoChatInputPanel
          session={session}
          running={running}
          setRunning={setRunning}
          messageHistory={messageHistory}
          setMessageHistory={(history) => setMessageHistory(history)}
          configuration={configuration}
          setConfiguration={setConfiguration}
        />
      </div>
    </div>
  );
}
