import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  Download,
  FileWarning,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  ShieldQuestion
} from "lucide-react";
import { getLatestReport, type ReportResponse } from "../api/analysis";
import { listProjects, type Project } from "../api/projects";
import { downloadExport } from "../api/reports";
import "../styles/risk.css";

type RiskLevel = "high" | "medium" | "low";

interface RiskItem {
  level: RiskLevel | string;
  category: string;
  title: string;
  source_page?: number | null;
  original_text: string;
  negative_impact: string;
  mitigation: string;
}

interface RiskReviewerResult {
  risks?: RiskItem[];
  summary?: {
    high?: number;
    medium?: number;
    low?: number;
  };
}

const levelConfig = {
  high: {
    title: "高风险",
    desc: "可能导致废标或重大合规问题",
    icon: ShieldAlert
  },
  medium: {
    title: "中风险",
    desc: "可能抬高成本或影响交付",
    icon: FileWarning
  },
  low: {
    title: "低风险",
    desc: "可通过澄清或商务沟通优化",
    icon: ShieldQuestion
  }
};

function extractRiskResult(report: ReportResponse | null): RiskReviewerResult {
  const finalReport = report?.final_report as Record<string, unknown> | undefined;
  const agents = finalReport?.agents as Record<string, unknown> | undefined;
  return (agents?.risk_reviewer as RiskReviewerResult | undefined) || {};
}

export function RiskPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
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
    loadRiskReport(selectedProjectId);
  }, [selectedProjectId]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  const riskResult = useMemo(() => extractRiskResult(report), [report]);
  const risks = riskResult.risks || [];
  const summary = {
    high: riskResult.summary?.high ?? risks.filter((risk) => risk.level === "high").length,
    medium: riskResult.summary?.medium ?? risks.filter((risk) => risk.level === "medium").length,
    low: riskResult.summary?.low ?? risks.filter((risk) => risk.level === "low").length
  };

  const groupedRisks = {
    high: risks.filter((risk) => risk.level === "high"),
    medium: risks.filter((risk) => risk.level === "medium"),
    low: risks.filter((risk) => risk.level === "low")
  };

  async function loadRiskReport(projectId = selectedProjectId) {
    if (!projectId) return;
    setLoadingReport(true);
    setError("");
    try {
      const data = await getLatestReport(projectId);
      setReport(data);
    } catch (err) {
      setReport(null);
      setError(err instanceof Error ? err.message : "暂未找到风险报告，请先执行分析");
    } finally {
      setLoadingReport(false);
    }
  }

  return (
    <main className="risk-page">
      <header className="risk-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="risk-eyebrow">风险审查 Agent</p>
          <h1>投标风险审查</h1>
          <p>自动分级识别废标、成本、交付和商务风险，并保留原文依据。</p>
        </div>
      </header>

      <section className="risk-toolbar">
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
        <button onClick={() => loadRiskReport()} disabled={!selectedProjectId || loadingReport}>
          <RefreshCw size={18} className={loadingReport ? "spin" : ""} />
          刷新
        </button>
        <button onClick={() => downloadExport(selectedProjectId, "risk-pdf")} disabled={!selectedProjectId}>
          <Download size={18} />
          导出PDF
        </button>
      </section>

      <section className="risk-summary-grid">
        {(["high", "medium", "low"] as RiskLevel[]).map((level) => {
          const config = levelConfig[level];
          const Icon = config.icon;
          return (
            <article className={`risk-summary-card ${level}`} key={level}>
              <div className="risk-summary-icon">
                <Icon size={22} />
              </div>
              <div>
                <span>{config.title}</span>
                <strong>{summary[level]}</strong>
                <p>{config.desc}</p>
              </div>
            </article>
          );
        })}
      </section>

      {error && (
        <div className="risk-alert">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button onClick={() => navigate("/analysis")}>去分析</button>
        </div>
      )}

      <section className="risk-context">
        <div>
          <span>当前项目</span>
          <strong>{selectedProject?.name || "未选择项目"}</strong>
        </div>
        <div>
          <span>分析编号</span>
          <strong>{report?.analysis_id || "暂无"}</strong>
        </div>
        <div>
          <span>审查状态</span>
          <strong>{risks.length > 0 ? "已生成" : "暂无结果"}</strong>
        </div>
      </section>

      <section className="risk-groups">
        {(["high", "medium", "low"] as RiskLevel[]).map((level) => {
          const config = levelConfig[level];
          const items = groupedRisks[level];
          const Icon = config.icon;
          return (
            <article className="risk-group" key={level}>
              <div className={`risk-group-title ${level}`}>
                <Icon size={20} />
                <div>
                  <h2>{config.title}</h2>
                  <p>{items.length}条</p>
                </div>
              </div>

              {items.length === 0 ? (
                <div className="empty-risk">
                  <ShieldCheck size={20} />
                  <span>最新报告中暂未发现该级别风险。</span>
                </div>
              ) : (
                <div className="risk-list">
                  {items.map((risk, index) => (
                    <div className="risk-item" key={`${risk.level}-${risk.category}-${index}`}>
                      <div className="risk-item-head">
                        <div>
                          <h3>{risk.title}</h3>
                          <span>{risk.category}</span>
                        </div>
                        <strong>{risk.source_page ? `第${risk.source_page}页` : "无页码"}</strong>
                      </div>
                      <dl>
                        <dt>原文依据</dt>
                        <dd>{risk.original_text}</dd>
                        <dt>负面影响</dt>
                        <dd>{risk.negative_impact}</dd>
                        <dt>规避建议</dt>
                        <dd>{risk.mitigation}</dd>
                      </dl>
                    </div>
                  ))}
                </div>
              )}
            </article>
          );
        })}
      </section>
    </main>
  );
}
