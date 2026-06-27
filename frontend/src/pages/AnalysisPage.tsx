import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Download,
  FileSearch,
  FileText,
  Loader2,
  Play,
  RefreshCw,
  ShieldAlert
} from "lucide-react";
import { getAnalysisTask, getLatestReport, startAnalysis, type AnalysisTask, type ReportResponse } from "../api/analysis";
import { listProjects, type Project } from "../api/projects";
import { downloadExport } from "../api/reports";
import { useToast } from "../components/ToastProvider";
import "../styles/analysis.css";

const agentSteps = [
  {
    key: "pdf_parser",
    title: "PDF文档解析 Agent",
    desc: "OCR识别扫描件，抽取正文、表格与关键招标字段。",
    icon: FileSearch
  },
  {
    key: "qualification_matcher",
    title: "资质匹配打分 Agent",
    desc: "逐条校验硬性门槛，计算企业投标匹配度。",
    icon: ClipboardCheck
  },
  {
    key: "risk_reviewer",
    title: "投标风险审查 Agent",
    desc: "识别高、中、低风险条款并给出应对建议。",
    icon: ShieldAlert
  },
  {
    key: "proposal_writer",
    title: "投标方案生成 Agent",
    desc: "生成商务标、技术标大纲和Markdown初稿。",
    icon: FileText
  }
];

const progressLabels: Record<string, string> = {
  router_started: "Router已启动",
  pdf_parser: "PDF解析中",
  pdf_parser_completed: "PDF解析完成",
  qualification_matcher: "资质匹配中",
  qualification_matcher_completed: "资质匹配完成",
  risk_reviewer: "风险审查中",
  risk_reviewer_completed: "风险审查完成",
  proposal_writer: "方案生成中",
  proposal_writer_completed: "方案生成完成",
  report_building: "正在汇总研判报告",
  completed: "分析完成"
};

const stepProgress: Record<string, number> = {
  router_started: 5,
  pdf_parser: 10,
  pdf_parser_completed: 30,
  qualification_matcher: 35,
  qualification_matcher_completed: 55,
  risk_reviewer: 60,
  risk_reviewer_completed: 75,
  proposal_writer: 80,
  proposal_writer_completed: 90,
  report_building: 95,
  completed: 100
};

const statusText: Record<string, string> = {
  idle: "待启动",
  pending: "等待中",
  running: "运行中",
  completed: "已完成",
  failed: "失败"
};

const stepStateText: Record<string, string> = {
  pending: "待执行",
  active: "执行中",
  completed: "已完成",
  failed: "失败"
};

export function AnalysisPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisTask | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [running, setRunning] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

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
        const msg = err instanceof Error ? err.message : "项目列表加载失败";
        setError(msg);
        showToast(msg, "error");
      })
      .finally(() => {
        if (mounted) setLoadingProjects(false);
      });
    return () => {
      mounted = false;
    };
  }, [showToast]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  const completed = analysis?.status === "completed";
  const failed = analysis?.status === "failed";
  const currentProgress = analysis?.progress ?? 0;
  const currentStep = analysis?.current_step || "router_started";

  async function handleStartAnalysis() {
    if (!selectedProjectId) {
      setError("请先选择一个项目");
      showToast("请先选择一个项目", "error");
      return;
    }
    setRunning(true);
    setError("");
    setMessage("");
    setReport(null);
    setAnalysis({
      id: "pending",
      project_id: selectedProjectId,
      status: "running",
      progress: 5,
      current_step: "router_started",
      created_at: new Date().toISOString()
    });

    try {
      const started = await startAnalysis(selectedProjectId);
      const latest = await getAnalysisTask(started.task_id);
      setAnalysis(latest);
      if (latest.status === "completed") {
        setMessage("多Agent分析已完成");
        showToast("多Agent分析已完成", "success");
        await loadReport(selectedProjectId);
      } else if (latest.status === "failed") {
        setError(latest.error_message || "分析失败");
        showToast(latest.error_message || "分析失败", "error");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "分析启动失败";
      setError(msg);
      showToast(msg, "error");
      setAnalysis(null);
    } finally {
      setRunning(false);
    }
  }

  async function loadReport(projectId = selectedProjectId) {
    if (!projectId) return;
    setLoadingReport(true);
    setError("");
    try {
      const data = await getLatestReport(projectId);
      setReport(data);
      showToast("报告已刷新", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "报告加载失败";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setLoadingReport(false);
    }
  }

  function stepState(index: number) {
    if (failed) return index === 0 ? "failed" : "pending";
    if (completed) return "completed";
    const progress = stepProgress[currentStep] ?? currentProgress;
    const thresholds = [10, 35, 60, 80];
    const completedThresholds = [30, 55, 75, 90];
    if (progress >= completedThresholds[index]) return "completed";
    if (progress >= thresholds[index]) return "active";
    return "pending";
  }

  return (
    <main className="analysis-page">
      <header className="analysis-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="analysis-eyebrow">Router总调度</p>
          <h1>多Agent自动研判</h1>
          <p>上传资料后由Router串联四个Skill Agent，自动完成投标可行性分析。</p>
        </div>
      </header>

      <section className="analysis-layout">
        <aside className="analysis-side">
          <div className="side-title">
            <Bot size={22} />
            <div>
              <h2>任务控制台</h2>
              <p>选择项目并启动完整分析链路</p>
            </div>
          </div>

          <label className="analysis-select">
            <span>分析项目</span>
            <select
              value={selectedProjectId}
              onChange={(event) => {
                setSelectedProjectId(event.target.value);
                setAnalysis(null);
                setReport(null);
                setError("");
                setMessage("");
              }}
              disabled={loadingProjects || running}
            >
              <option value="">请选择项目</option>
              {projects.map((project) => (
                <option value={project.id} key={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>

          <div className="project-summary">
            <span>状态</span>
            <strong>{selectedProject?.status || "未选择"}</strong>
            <span>最近得分</span>
            <strong>{selectedProject?.latest_score ?? "-"}</strong>
            <span>研判结论</span>
            <strong>{selectedProject?.latest_recommendation || "-"}</strong>
          </div>

          <button className="primary-action" onClick={handleStartAnalysis} disabled={!selectedProjectId || running}>
            {running ? <Loader2 size={18} className="spin" /> : <Play size={18} />}
            {running ? "Router运行中" : "开始分析"}
          </button>

          <button className="secondary-action" onClick={() => loadReport()} disabled={!selectedProjectId || loadingReport}>
            {loadingReport ? <Loader2 size={18} className="spin" /> : <RefreshCw size={18} />}
            刷新报告
          </button>

          <button className="secondary-action" onClick={() => downloadExport(selectedProjectId, "qualification-excel")} disabled={!selectedProjectId}>
            <Download size={18} />
            导出资质Excel
          </button>

          <button className="secondary-action" onClick={() => downloadExport(selectedProjectId, "all")} disabled={!selectedProjectId}>
            <Download size={18} />
            导出全部文件
          </button>
        </aside>

        <section className="analysis-main">
          <div className="analysis-card">
            <div className="card-row">
              <div>
                <h2>{selectedProject?.name || "请选择项目"}</h2>
                <p>{progressLabels[currentStep] || currentStep}</p>
              </div>
              <div className={`analysis-status ${analysis?.status || "idle"}`}>
                {completed && <CheckCircle2 size={16} />}
                {failed && <AlertTriangle size={16} />}
                {running && <Loader2 size={16} className="spin" />}
                {statusText[analysis?.status || "idle"] || analysis?.status || "待启动"}
              </div>
            </div>

            <div className="progress-track">
              <div style={{ width: `${Math.min(100, Math.max(0, currentProgress))}%` }} />
            </div>
            {running && (
              <div className="analysis-running">
                <Loader2 size={18} className="spin" />
                Router正在调度各个Skill Agent，请稍候...
              </div>
            )}
            <div className="progress-meta">
              <span>{currentProgress}%</span>
              <span>{analysis?.finished_at ? `完成时间 ${new Date(analysis.finished_at).toLocaleString()}` : "等待完成"}</span>
            </div>

            {(error || message) && <div className={error ? "analysis-alert error" : "analysis-alert success"}>{error || message}</div>}
          </div>

          <div className="agent-grid">
            {agentSteps.map((step, index) => {
              const Icon = step.icon;
              const state = stepState(index);
              return (
                <article className={`agent-card ${state}`} key={step.key}>
                  <div className="agent-icon">
                    <Icon size={22} />
                  </div>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.desc}</p>
                    <span>{stepStateText[state] || state}</span>
                  </div>
                </article>
              );
            })}
          </div>

          <section className="result-grid">
            <article className="result-card">
              <BarChart3 size={22} />
              <span>匹配得分</span>
              <strong>{analysis?.score ?? "-"}</strong>
            </article>
            <article className="result-card wide">
              <FileText size={22} />
              <span>研判建议</span>
              <strong>{analysis?.recommendation || "完成分析后生成建议"}</strong>
              {analysis?.summary && <p>{analysis.summary}</p>}
            </article>
          </section>

          {report && (
            <section className="report-preview">
              <div className="card-row">
                <div>
                  <h2>完整报告预览</h2>
                  <p>以下内容来自Router最终汇总结果</p>
                </div>
                <span>{report.analysis_id}</span>
              </div>
              <pre>{JSON.stringify(report.final_report, null, 2)}</pre>
            </section>
          )}
        </section>
      </section>
    </main>
  );
}
