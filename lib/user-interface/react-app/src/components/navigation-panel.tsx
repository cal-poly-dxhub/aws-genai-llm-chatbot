import {
  SideNavigation,
  SideNavigationProps,
} from "@cloudscape-design/components";
import useOnFollow from "../common/hooks/use-on-follow";
import { useNavigationPanelState } from "../common/hooks/use-navigation-panel-state";
import { AppContext } from "../common/app-context";
import { useContext, useState } from "react";
import { PLUGIN_ECISO_CHATBOT_NAME,CHATBOT_NAME } from "../common/constants";

export default function NavigationPanel() {
  const appContext = useContext(AppContext);
  const onFollow = useOnFollow();
  const [navigationPanelState, setNavigationPanelState] =
    useNavigationPanelState();

  const [items] = useState<SideNavigationProps.Item[]>(() => {

    const items: SideNavigationProps.Item[] = [
      {
        type: "link",
        text: "Home",
        href: "/",
      },
      {
        type: "section",
        text: "Chatbot",
        items: [
          { type: "link", text: "Playground", href: "/chatbot/playground" },
          {
            type: "link",
            text: "Multi-chat playground",
            href: "/chatbot/multichat",
          },
          {
            type: "link",
            text: "Models",
            href: "/chatbot/models",
          },
        ],
      },
    ];
    console.log("NAV <rag_enabled>: ",appContext?.config.rag_enabled)
    console.log("NAV <eciso_enabed>: ",appContext?.config.custom_plugins)
    console.log("NAV <eciso_enabed>: ",appContext?.config.eciso_enabled)
    console.log("NAV <eciso_enabed_focus>: ",appContext?.config.eciso_focus_enabled)
    if (appContext?.config.custom_plugins) {

      items.push(
        { type: "divider" },
        {
          type: "section",
          text: "Custom Plugins",
          items: appContext?.config.eciso_enabled ? 
            [ 
              { type: "link", text: "eCISO Home", href: "/plugins/eciso-home" },
              { type: "link", text: "eCISO Chat", href: "/plugins/eciso" },
            ]: []
        },
      
      );      
    }

    if (appContext?.config.rag_enabled) {
      const crossEncodersItems: SideNavigationProps.Item[] = appContext?.config
        .cross_encoders_enabled
        ? [
            {
              type: "link",
              text: "Cross-encoders",
              href: "/rag/cross-encoders",
            },
          ]
        : [];

      items.push({
        type: "section",
        text: "Retrieval-Augmented Generation (RAG)",
        items: [
          { type: "link", text: "Dashboard", href: "/rag" },
          {
            type: "link",
            text: "Semantic search",
            href: "/rag/semantic-search",
          },
          { type: "link", text: "Workspaces", href: "/rag/workspaces" },
          {
            type: "link",
            text: "Embeddings",
            href: "/rag/embeddings",
          },
          ...crossEncodersItems,
          { type: "link", text: "Engines", href: "/rag/engines" },
        ],
      });
    }

    items.push(
      { type: "divider" },
      {
        type: "link",
        text: "Documentation",
        href: "https://aws-samples.github.io/aws-genai-llm-chatbot/",
        external: true,
      }
    );

    //cheap dirty code to build focus mode
    if( appContext?.config.eciso_focus_enabled ){
      items.length = 0;
      items.push(
        {
          type: "link",
          text: "Home",
          href: "/",
        },
        {
          type: "link",
          text: PLUGIN_ECISO_CHATBOT_NAME,
          href: "/plugins/eciso",
        },
      )
    }

    return items;
  });

  const onChange = ({
    detail,
  }: {
    detail: SideNavigationProps.ChangeDetail;
  }) => {
    const sectionIndex = items.indexOf(detail.item);
    setNavigationPanelState({
      collapsedSections: {
        ...navigationPanelState.collapsedSections,
        [sectionIndex]: !detail.expanded,
      },
    });
  };

  return (
    <SideNavigation
      onFollow={onFollow}
      onChange={onChange}
      header={{ href: "/", text: CHATBOT_NAME }}
      items={items.map((value, idx) => {
        if (value.type === "section") {
          const collapsed =
            navigationPanelState.collapsedSections?.[idx] === true;
          value.defaultExpanded = !collapsed;
        }

        return value;
      })}
    />
  );
}
