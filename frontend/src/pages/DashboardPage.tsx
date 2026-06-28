import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  FileText,
  FileUp,
  FolderKanban,
  LogOut,
  Plus,
  Settings,
  ShieldCheck,
  Timer,
  TrendingUp
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
  { label: "PDF 解析", desc: "抽取全文、表格、页码和关键条款", icon: FileText },
  { label: "资质匹配", desc: "校验硬性门槛并计算匹配得分", icon: ShieldCheck },
  { label: "风险审查", desc: "识别废标、成本和合同风险", icon: AlertTriangle },
  { label: "方案生成", desc: "生成商务标与技术标写作初稿", icon: Bot }
];

const statusLabel: Record<string, string> = {
  draft: "草稿",
  created: "已创建",
  partial_uploaded: "待补文件",
  uploaded: "资料已上传",
  analyzing: "分析中",
  completed: "已完成",
  failed: "失败"
};

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
      { label: "项目总数", value: summary.project_count, icon: FolderKanban, tone: "teal", hint: "全部投标项目" },
      { label: "已完成", value: summary.completed_count, icon: CheckCircle2, tone: "green", hint: "已生成研判报告" },
      { label: "运行中", value: summary.running_count, icon: Timer, tone: "blue", hint: "Agent 正在处理" },
      { label: "高风险", value: summary.high_risk_count ?? 0, icon: AlertTriangle, tone: "amber", hint: "需优先复核" }
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
        <div className="header-copy">
          <p className="dashboard-eyebrow">AI 招投标多智能体系统</p>
          <h1>企业投标研判工作台</h1>
          <p>
            欢迎回来，{user?.username || "用户"}。从资料上传到风险审查、资质评分、投标方案生成，
            全流程由 Router 调度四个独立 Agent 自动完成。
          </p>
        </div>
        <div className="header-actions">
          <button className="ghost-button" onClick={() => navigate("/admin")}>
            <Settings size={18} />
            管理后台
          </button>
          <button className="ghost-button danger" onClick={logout}>
            <LogOut size={18} />
            退出
          </button>
        </div>
      </header>

      <section className="hero-command">
        <div>
          <span className="command-label">Router Orchestration</span>
          <h2>上传 PDF 后，系统自动完成投标可行性研判</h2>
          <p>支持招标解析、资质台账匹配、风险分级、投标初稿生成和报告导出，适合现场路演直接演示完整闭环。</p>
        </div>
        <button onClick={() => navigate("/upload")}>
          <Plus size={18} />
          新建投标项目
        </button>
      </section>

      <section className="status-strip">
        <span>{loading ? "正在加载工作台数据..." : apiStatus}</span>
        <strong>JWT 已启用 · API 已连接</strong>
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
              <div className="metric-top">
                <div className="metric-icon">
                  <Icon size={20} />
                </div>
                <span>{card.hint}</span>
              </div>
              <p>{card.label}</p>
              <strong>{card.value}</strong>
            </article>
          );
        })}
      </section>

      <section className="dashboard-main">
        <article className="work-panel">
          <div className="panel-heading">
            <div>
              <h2>多 Agent 执行链路</h2>
              <p>四个 Skill 完全解耦，可独立调试，也可由 Router 串联执行。</p>
            </div>
            <button className="link-button" onClick={() => navigate("/analysis")}>
              开始分析
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="agent-flow">
            {agentSteps.map((step, index) => {
              const Icon = step.icon;
              return (
                <button
                  className="agent-step"
                  key={step.label}
                  onClick={step.label === "方案生成" ? () => navigate("/proposal") : undefined}
                >
                  <div className="step-index">{index + 1}</div>
                  <Icon size={18} />
                  <div>
                    <strong>{step.label}</strong>
                    <span>{step.desc}</span>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="quick-actions">
            <button onClick={() => navigate("/upload")}>
              <FileUp size={18} />
              上传资料
            </button>
            <button className="secondary" onClick={() => navigate("/risks")}>
              <AlertTriangle size={18} />
              查看风险
            </button>
            <button className="secondary" onClick={() => navigate("/history")}>
              <FolderKanban size={18} />
              历史记录
            </button>
          </div>
        </article>

        <article className="work-panel insight-panel">
          <div className="panel-heading">
            <div>
              <h2>分析概览</h2>
              <p>匹配得分与风险态势。</p>
            </div>
            <BarChart3 size={22} />
          </div>
          <div className="score-box">
            <span>平均匹配分</span>
            <strong>{summary.average_score ?? 0}</strong>
            <p>优先补齐硬性材料，再优化技术响应与可量化证明。</p>
          </div>
          <div className="trend-card">
            <TrendingUp size={18} />
            <span>建议重点关注废标条款、保证金、人员社保与同类业绩证明。</span>
          </div>
        </article>
      </section>

      <section className="projects-panel">
        <div className="panel-heading">
          <div>
            <h2>最近项目</h2>
            <p>查看近期投标分析记录和处理状态。</p>
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
            <span>文件</span>
            <span>创建时间</span>
          </div>
          {loading && (
            <div className="project-loading">
              <span className="loader-dot" />
              正在加载最近项目...
            </div>
          )}
          {!loading && projects.length === 0 && (
            <div className="empty-state">
              <strong>还没有项目</strong>
              <span>请先上传招标 PDF 和企业资质台账，创建第一条投标研判记录。</span>
              <button onClick={() => navigate("/upload")}>立即上传</button>
            </div>
          )}
          {projects.map((project) => (
            <div className="project-row" key={project.id}>
              <strong>{project.name}</strong>
              <span>{project.tender_company || project.tender_name || project.enterprise_id}</span>
              <span className={`status-pill ${project.status}`}>{statusLabel[project.status] || project.status}</span>
              <span>{project.latest_score ?? "-"}</span>
              <span>{project.files_ready ? "已齐全" : "待补充"}</span>
              <span>{new Date(project.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
