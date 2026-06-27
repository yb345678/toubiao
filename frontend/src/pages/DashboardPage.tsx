import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  Settings,
  FileUp,
  FolderKanban,
  LogOut,
  Plus,
  Timer
} from "lucide-react";
import { getDashboardSummary, type DashboardSummary } from "../api/dashboard";
import { listProjects, type Project } from "../api/projects";
import { useToast } from "../components/ToastProvider";
import { clearToken, getCachedUser } from "../store/authStore";
import "../styles/dashboard.css";

const fallbackSummary: DashboardSummary = {
  project_count: 0,
  completed_count: 0,
  running_count: 0,
  average_score: 0,
  high_risk_count: 0
};

const agentSteps = [
  { label: "PDF 解析", desc: "全文、表格与页码溯源" },
  { label: "资质匹配", desc: "硬性门槛与评分计算" },
  { label: "风险审查", desc: "废标、成本与合同风险" },
  { label: "投标方案", desc: "商务标与技术标初稿" }
];

export function DashboardPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const user = getCachedUser();
  const [summary, setSummary] = useState<DashboardSummary>(fallbackSummary);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState("正在同步后端数据...");

  useEffect(() => {
    let mounted = true;
    Promise.all([getDashboardSummary(), listProjects()])
      .then(([data, projectData]) => {
        if (!mounted) return;
        setSummary({ ...fallbackSummary, ...data });
        setProjects(projectData.slice(0, 5));
        setApiStatus("后端数据已同步");
      })
      .catch((err) => {
        if (!mounted) return;
        const msg = err instanceof Error ? err.message : "后端服务未连接";
        setApiStatus(msg);
        showToast(msg, "error");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [showToast]);

  const cards = useMemo(
    () => [
      { label: "项目总数", value: summary.project_count, icon: FolderKanban, tone: "teal" },
      { label: "已完成", value: summary.completed_count, icon: CheckCircle2, tone: "green" },
      { label: "运行中", value: summary.running_count, icon: Timer, tone: "blue" },
      { label: "高风险", value: summary.high_risk_count ?? 0, icon: AlertTriangle, tone: "amber" }
    ],
    [summary]
  );

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">AI 招投标多智能体系统</p>
          <h1>投标研判工作台</h1>
          <p>
            欢迎回来，{user?.username || "用户"}。创建项目、上传招标文件，
            即可启动多 Agent 投标分析流程。
          </p>
        </div>
        <button className="ghost-button" onClick={logout}>
          <LogOut size={18} />
          退出
        </button>
        <button className="ghost-button" onClick={() => navigate("/admin")}>
          <Settings size={18} />
          管理后台
        </button>
      </header>

      <section className="status-strip">
        <span>{loading ? "正在加载工作台数据..." : apiStatus}</span>
        <strong>JWT 已启用</strong>
      </section>

      <section className="metric-grid">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <article
              className={`metric-card ${card.tone}`}
              key={card.label}
              onClick={card.label === "高风险" ? () => navigate("/risks") : undefined}
            >
              <div className="metric-icon">
                <Icon size={20} />
              </div>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
            </article>
          );
        })}
      </section>

      <section className="dashboard-main">
        <article className="work-panel">
          <div className="panel-heading">
            <div>
              <h2>快速开始</h2>
              <p>创建投标项目，上传招标 PDF 与企业资质台账。</p>
            </div>
          </div>
          <div className="quick-actions">
            <button onClick={() => navigate("/upload")}>
              <Plus size={18} />
              新建项目
            </button>
            <button className="secondary" onClick={() => navigate("/upload")}>
              <FileUp size={18} />
              上传文件
            </button>
            <button className="secondary" onClick={() => navigate("/analysis")}>
              <Bot size={18} />
              开始分析
            </button>
          </div>

          <div className="agent-flow">
            {agentSteps.map((step, index) => (
              <button
                className="agent-step"
                key={step.label}
                onClick={step.label === "投标方案" ? () => navigate("/proposal") : undefined}
              >
                <div className="step-index">{index + 1}</div>
                <div>
                  <strong>{step.label}</strong>
                  <span>{step.desc}</span>
                </div>
              </button>
            ))}
          </div>
        </article>

        <article className="work-panel">
          <div className="panel-heading">
            <div>
              <h2>分析概览</h2>
              <p>系统汇总匹配分数、风险数量与投标建议。</p>
            </div>
            <BarChart3 size={22} />
          </div>
          <div className="score-box">
            <span>平均匹配分</span>
            <strong>{summary.average_score ?? 0}</strong>
            <p>优先补齐硬性材料，再优化技术响应与可量化证明。</p>
          </div>
        </article>
      </section>

      <section className="projects-panel">
        <div className="panel-heading">
          <div>
            <h2>最近项目</h2>
            <p>查看近期投标分析记录。</p>
          </div>
          <button className="link-button" onClick={() => navigate("/history")}>
            全部项目
            <ArrowRight size={16} />
          </button>
        </div>
        <div className="project-table">
          <div className="project-row header">
            <span>项目</span>
            <span>招标单位</span>
            <span>状态</span>
            <span>分数</span>
            <span>高风险</span>
            <span>更新时间</span>
          </div>
          {loading && (
            <div className="project-loading">
              <span className="loader-dot" />
              正在加载最近项目...
            </div>
          )}
          {!loading && projects.length === 0 && (
            <div className="project-loading">暂无项目，请先上传文件创建项目。</div>
          )}
          {projects.map((project) => (
            <div className="project-row" key={project.id}>
              <strong>{project.name}</strong>
              <span>{project.tender_company || project.tender_name || project.enterprise_id}</span>
              <span className={`status-pill ${project.status}`}>{project.status}</span>
              <span>{project.latest_score ?? "-"}</span>
              <span>{summary.high_risk_count ?? "-"}</span>
              <span>{new Date(project.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
