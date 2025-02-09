import {
  Box,
  Button,
  Container,
  ExpandableSection,
  Popover,
  Spinner,
  StatusIndicator,
  Tabs,
  TextContent,
  Textarea,
} from "@cloudscape-design/components";
import { useEffect, useState } from "react";
import { JsonView, darkStyles } from "react-json-view-lite";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "../../styles/chat.module.scss";
import {
  ChatBotConfiguration,
  ChatBotHistoryItem,
  ChatBotMessageType,
  ImageFile,
  RagDocument,
} from "./types";

import { getSignedUrl } from "./utils";

import "react-json-view-lite/dist/index.css";
import "../../styles/app.scss";
import { FaThumbsUp, FaThumbsDown } from "react-icons/fa";

export interface ChatMessageProps {
  message: ChatBotHistoryItem;
  configuration?: ChatBotConfiguration;
  showMetadata?: boolean;
  onThumbsUp: () => void;
  onThumbsDown: () => void;
}

export default function ChatMessage(props: ChatMessageProps) {
  const [loading, setLoading] = useState<boolean>(false);
  const [message] = useState<ChatBotHistoryItem>(props.message);
  const [files, setFiles] = useState<ImageFile[]>([] as ImageFile[]);
  const [documentIndex, setDocumentIndex] = useState("0");
  const [promptIndex, setPromptIndex] = useState("0");
  const [selectedIcon, setSelectedIcon] = useState<1 | 0 | null>(null);

  useEffect(() => {
    const getSignedUrls = async () => {
      setLoading(true);
      if (message.metadata?.files as ImageFile[]) {
        const files: ImageFile[] = [];
        for await (const file of message.metadata?.files as ImageFile[]) {
          const signedUrl = await getSignedUrl(file.key);
          files.push({
            ...file,
            url: signedUrl as string,
          });
        }

        setLoading(false);
        setFiles(files);
      }
    };

    if (message.metadata?.files as ImageFile[]) {
      getSignedUrls();
    }
  }, [message]);

  return (
    <div>
      {props.message?.type === ChatBotMessageType.AI && (
        <Container
          footer={
            ((props?.showMetadata && props.message.metadata) ||
              (props.message.metadata &&
                props.configuration?.showMetadata)) && (
              <ExpandableSection variant="footer" headerText="Metadata">
                <JsonView
                  shouldInitiallyExpand={(level) => level < 2}
                  data={JSON.parse(
                    JSON.stringify(props.message.metadata).replace(
                      /\\n/g,
                      "\\\\n"
                    )
                  )}
                  style={{
                    ...darkStyles,
                    stringValue: "jsonStrings",
                    numberValue: "jsonNumbers",
                    booleanValue: "jsonBool",
                    nullValue: "jsonNull",
                    container: "jsonContainer",
                  }}
                />
                {props.message.metadata.documents && (
                  <>
                    <div className={styles.btn_chabot_metadata_copy}>
                      <Popover
                        size="medium"
                        position="top"
                        triggerType="custom"
                        dismissButton={false}
                        content={
                          <StatusIndicator type="success">
                            Copied to clipboard
                          </StatusIndicator>
                        }
                      >
                        <Button
                          variant="inline-icon"
                          iconName="copy"
                          onClick={() => {
                            navigator.clipboard.writeText(
                              (
                                props.message.metadata
                                  .documents as RagDocument[]
                              )[parseInt(documentIndex)].page_content
                            );
                          }}
                        />
                      </Popover>
                    </div>
                    <Tabs
                      tabs={(
                        props.message.metadata.documents as RagDocument[]
                      ).map((p: any, i) => {
                        return {
                          id: `${i}`,
                          label: p.metadata.path,
                          content: (
                            <>
                              <Textarea
                                value={p.page_content}
                                readOnly={true}
                                rows={8}
                              />
                            </>
                          ),
                        };
                      })}
                      activeTabId={documentIndex}
                      onChange={({ detail }) =>
                        setDocumentIndex(detail.activeTabId)
                      }
                    />
                  </>
                )}
                {props.message.metadata.prompts && (
                  <>
                    <div className={styles.btn_chabot_metadata_copy}>
                      <Popover
                        size="medium"
                        position="top"
                        triggerType="custom"
                        dismissButton={false}
                        content={
                          <StatusIndicator type="success">
                            Copied to clipboard
                          </StatusIndicator>
                        }
                      >
                        <Button
                          variant="inline-icon"
                          iconName="copy"
                          onClick={() => {
                            navigator.clipboard.writeText(
                              (props.message.metadata.prompts as string[][])[
                                parseInt(promptIndex)
                              ][0]
                            );
                          }}
                        />
                      </Popover>
                    </div>
                    <Tabs
                      tabs={(props.message.metadata.prompts as string[][]).map(
                        (p, i) => {
                          return {
                            id: `${i}`,
                            label: `Prompt ${
                              (props.message.metadata.prompts as string[][])
                                .length > 1
                                ? i + 1
                                : ""
                            }`,
                            content: (
                              <>
                                <Textarea
                                  value={p[0]}
                                  readOnly={true}
                                  rows={8}
                                />
                              </>
                            ),
                          };
                        }
                      )}
                      activeTabId={promptIndex}
                      onChange={({ detail }) =>
                        setPromptIndex(detail.activeTabId)
                      }
                    />
                  </>
                )}
              </ExpandableSection>
            )
          }
        >
          {props.message.content.length === 0 ? (
            <Box>
              <Spinner />
            </Box>
          ) : null}
          {props.message.content.length > 0 ? (
            <div className={styles.btn_chabot_message_copy}>
              <Popover
                size="medium"
                position="top"
                triggerType="custom"
                dismissButton={false}
                content={
                  <StatusIndicator type="success">
                    Copied to clipboard
                  </StatusIndicator>
                }
              >
                <Button
                  variant="inline-icon"
                  iconName="copy"
                  onClick={() => {
                    navigator.clipboard.writeText(props.message.content);
                  }}
                />
              </Popover>
            </div>
          ) : null}
          <ReactMarkdown
            children={props.message.content}
            remarkPlugins={[remarkGfm]}
            components={{
              pre(props) {
                const { children, className, node, ...rest } = props;
                return (
                  <pre {...rest} className={styles.codeMarkdown}>
                    {children}
                  </pre>
                );
              },
              table(props) {
                const { children, ...rest } = props;
                return (
                  <table {...rest} className={styles.markdownTable}>
                    {children}
                  </table>
                );
              },
              th(props) {
                const { children, ...rest } = props;
                return (
                  <th {...rest} className={styles.markdownTableCell}>
                    {children}
                  </th>
                );
              },
              td(props) {
                const { children, ...rest } = props;
                return (
                  <td {...rest} className={styles.markdownTableCell}>
                    {children}
                  </td>
                );
              },
            }}
          />
          <div className={styles.thumbsContainer}>
            {(selectedIcon === 1 || selectedIcon === null) && (
              <FaThumbsUp
                className={`${styles.thumbsIcon} ${styles.thumbsUp} ${selectedIcon === 1 ? styles.selected : ''}`}
                onClick={() => {
                  props.onThumbsUp();
                  setSelectedIcon(1);
                }}
              />
            )}
            {(selectedIcon === 0 || selectedIcon === null) && (
              <FaThumbsDown
                className={`${styles.thumbsIcon} ${styles.thumbsDown} ${selectedIcon === 0 ? styles.selected : ''}`}
                onClick={() => {
                  props.onThumbsDown();
                  setSelectedIcon(0);
                }}
              />
            )}
          </div>
        </Container>
      )}
      {loading && (
        <Box float="left">
          <Spinner />
        </Box>
      )}
      {files && !loading && (
        <>
          {files.map((file, idx) => (
            <a
              key={idx}
              href={file.url as string}
              target="_blank"
              rel="noreferrer"
            >
              <img
                src={file.url as string}
                className={styles.img_chabot_message}
              />
            </a>
          ))}
        </>
      )}
      {props.message?.type === ChatBotMessageType.Human && (
        <TextContent>
          <strong>{props.message.content}</strong>
        </TextContent>
      )}
    </div>
  );
}
