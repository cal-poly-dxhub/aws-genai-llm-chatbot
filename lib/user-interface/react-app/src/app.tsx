import { useContext } from "react";
import {
  BrowserRouter,
  HashRouter,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import { AppContext } from "./common/app-context";
import GlobalHeader from "./components/global-header";
import Models from "./pages/chatbot/models/models";
import MultiChatPlayground from "./pages/chatbot/playground/multi-chat-playground";
import Playground from "./pages/chatbot/playground/playground";
import NotFound from "./pages/not-found";
import AddData from "./pages/rag/add-data/add-data";
import CreateWorkspace from "./pages/rag/create-workspace/create-workspace";
import CrossEncoders from "./pages/rag/cross-encoders/cross-encoders";
import Dashboard from "./pages/rag/dashboard/dashboard";
import Embeddings from "./pages/rag/embeddings/embeddings";
import Engines from "./pages/rag/engines/engines";
import SemanticSearch from "./pages/rag/semantic-search/semantic-search";
import RssFeed from "./pages/rag/workspace/rss-feed";
import WorkspacePane from "./pages/rag/workspace/workspace";
import Workspaces from "./pages/rag/workspaces/workspaces";
import Welcome from "./pages/welcome";
import Eciso from "./pages/plugins/eciso/eciso";
import EcisoWelcome from "./pages/plugins/eciso/eciso-welcome";
import "./styles/app.scss";

function App() {
  const appContext = useContext(AppContext);
  const Router = appContext?.config.privateWebsite ? HashRouter : BrowserRouter;

  return (
    <div style={{ height: "100%" }}>
      <Router>
        <GlobalHeader />
        <div style={{ height: "56px", backgroundColor: "#000716" }}>&nbsp;</div>
        <div>
          <Routes>
            { appContext?.config.eciso_focus_enabled ?<Route index path="/" element={<EcisoWelcome />} />  :
              <Route index path="/" element={<Welcome />} />
            }
            { appContext?.config.eciso_focus_enabled ? <></> :
            <Route path="/chatbot" element={<Outlet />}>
              <Route path="playground" element={<Playground />} />
              <Route path="playground/:sessionId" element={<Playground />} />
              <Route path="multichat" element={<MultiChatPlayground />} />
              <Route path="models" element={<Models />} />
            </Route> 
            }
            { appContext?.config.eciso_focus_enabled ? <></> :
            <Route path="/rag" element={<Outlet />}>
              <Route path="" element={<Dashboard />} />
              <Route path="engines" element={<Engines />} />
              <Route path="embeddings" element={<Embeddings />} />
              <Route path="cross-encoders" element={<CrossEncoders />} />
              <Route path="semantic-search" element={<SemanticSearch />} />
              <Route path="workspaces" element={<Workspaces />} />
              <Route path="workspaces/create" element={<CreateWorkspace />} />
              <Route
                path="workspaces/:workspaceId"
                element={<WorkspacePane />}
              />
              
              <Route
                path="workspaces/:workspaceId/rss/:feedId"
                element={<RssFeed />}
              />
              <Route path="workspaces/add-data" element={<AddData />} />
            </Route>
            }
            <Route path="/plugins" element={<Outlet />}>
              { !appContext?.config.eciso_focus_enabled ? <Route path="eciso-home" element={<EcisoWelcome/>} /> : <></> }
              <Route path="eciso" element={<Eciso/>} />
              <Route path="eciso/:sessionId" element={<Eciso />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
}

export default App;
