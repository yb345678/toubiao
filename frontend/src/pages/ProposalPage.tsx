import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BriefcaseBusiness,
  ClipboardList,
  Copy,
  Download,
  FileEdit,
  FileText,
  RefreshCw,
  Sparkles
} from "lucide-react";
import { getLatestReport, type ReportResponse } from "../api/analysis";
import { listProjects, type Project } from "../api/projects";
import { downloadExport } from "../api/reports";
import "../styles/proposal.css";

interface ProposalWriterResult {
  business_outline?: string[];
  technical_outline?: string[];
  matched_materials?: string[];
  markdown_draft?: string;
}

function extractProposal(report: ReportResponse | null): ProposalWriterResult {
  const finalReport = report?.final_report as Record<string, unknown> | undefined;
  const agents = finalReport?.agents as Record<string, unknown> | undefined;
  return (agents?.proposal_writer as ProposalWriterResult | undefined) || {};
}

function downloadMarkdown(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function ProposalPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [draft, setDraft] = useState("");
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    listProjects()
      .then((data) => {
        if (!mounted) return;
        setProjects(data);
        if (data.length > 0) {
          setSelectedProjectId(data[0].id);
        }
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "项目列表加载失败");
      })
      .finally(() => {
        if (mounted) setLoadingProjects(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedProjectId) return;
    loadProposal(selectedProjectId);
  }, [selectedProjectId]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  const proposal = useMemo(() => extractProposal(report), [report]);
  const businessOutline = proposal.business_outline || [];
  const technicalOutline = proposal.technical_outline || [];
  const matchedMaterials = proposal.matched_materials || [];

  async function loadProposal(projectId = selectedProjectId) {
    if (!projectId) return;
    setLoadingReport(true);
    setError("");
    setMessage("");
    try {
      const data = await getLatestReport(projectId);
      const nextProposal = extractProposal(data);
      setReport(data);
      setDraft(nextProposal.markdown_draft || "");
      if (!nextProposal.markdown_draft) {
        setError("最新报告中暂未生成投标方案，请先执行分析。");
      }
    } catch (err) {
      setReport(null);
      setDraft("");
      setError(err instanceof Error ? err.message : "暂未找到投标方案，请先执行分析");
    } finally {
      setLoadingReport(false);
    }
  }

  async function copyDraft() {
    if (!draft) return;
    await navigator.clipboard.writeText(draft);
    setMessage("Markdown初稿已复制到剪贴板");
  }

  function exportDraft() {
    if (!draft) return;
    const safeName = (selectedProject?.name || "bid-proposal").replace(/[\\/:*?"<>|]/g, "-");
    downloadMarkdown(`${safeName}-proposal.md`, draft);
    setMessage("Markdown文件已导出");
  }

  return (
    <main className="proposal-page">
      <header className="proposal-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="proposal-eyebrow">方案生成 Agent</p>
          <h1>投标方案生成</h1>
          <p>根据评分细则和企业素材生成商务标、技术标大纲及Markdown初稿。</p>
        </div>
      </header>

      <section className="proposal-toolbar">
        <label>
          <span>项目</span>
          <select value={selectedProjectId} onChange={(event) => setSelectedProjectId(event.target.value)} disabled={loadingProjects || loadingReport}>
            <option value="">请选择项目</option>
            {projects.map((project) => (
              <option value={project.id} key={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </label>
        <button onClick={() => loadProposal()} disabled={!selectedProjectId || loadingReport}>
          <RefreshCw size={18} className={loadingReport ? "spin" : ""} />
          刷新
        </button>
        <button className="secondary" onClick={() => navigate("/analysis")}>
          <Sparkles size={18} />
          重新分析
        </button>
      </section>

      {(error || message) && <div className={error ? "proposal-alert error" : "proposal-alert success"}>{error || message}</div>}

      <section className="proposal-summary">
        <article>
          <span>当前项目</span>
          <strong>{selectedProject?.name || "未选择项目"}</strong>
        </article>
        <article>
          <span>分析编号</span>
          <strong>{report?.analysis_id || "暂无"}</strong>
        </article>
        <article>
          <span>匹配素材</span>
          <strong>{matchedMaterials.length}</strong>
        </article>
      </section>

      <section className="proposal-layout">
        <aside className="proposal-side">
          <div className="outline-block">
            <div className="outline-title">
              <BriefcaseBusiness size={20} />
              <h2>商务标大纲</h2>
            </div>
            <ol>{businessOutline.length > 0 ? businessOutline.map((item) => <li key={item}>{item}</li>) : <li>暂无商务标大纲</li>}</ol>
          </div>

          <div className="outline-block">
            <div className="outline-title">
              <ClipboardList size={20} />
              <h2>技术标大纲</h2>
            </div>
            <ol>{technicalOutline.length > 0 ? technicalOutline.map((item) => <li key={item}>{item}</li>) : <li>暂无技术标大纲</li>}</ol>
          </div>

          <div className="outline-block">
            <div className="outline-title">
              <FileText size={20} />
              <h2>匹配素材</h2>
            </div>
            <ul>{matchedMaterials.length > 0 ? matchedMaterials.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li>暂无匹配素材</li>}</ul>
          </div>
        </aside>

        <section className="draft-panel">
          <div className="draft-heading">
            <div>
              <h2>可编辑Markdown初稿</h2>
              <p>可直接修改内容，也可以导出为Markdown或Word文档。</p>
            </div>
            <div className="draft-actions">
              <button onClick={copyDraft} disabled={!draft}>
                <Copy size={17} />
                复制
              </button>
              <button onClick={exportDraft} disabled={!draft}>
                <Download size={17} />
                导出MD
              </button>
              <button onClick={() => downloadExport(selectedProjectId, "proposal-markdown")} disabled={!selectedProjectId}>
                <Download size={17} />
                下载Markdown
              </button>
              <button onClick={() => downloadExport(selectedProjectId, "proposal-word")} disabled={!selectedProjectId}>
                <Download size={17} />
                下载Word
              </button>
            </div>
          </div>

          <div className="editor-shell">
            <div className="editor-label">
              <FileEdit size={17} />
              proposal.md
            </div>
            <textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="完成分析后将在这里显示投标方案初稿" />
          </div>
        </section>
      </section>
    </main>
  );
}
