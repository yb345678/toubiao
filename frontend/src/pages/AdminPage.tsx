import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  Bot,
  CheckCircle2,
  Database,
  FileStack,
  KeyRound,
  Lock,
  RefreshCw,
  Server,
  Settings,
  ShieldCheck,
  Users
} from "lucide-react";
import { getSystemHealth, type HealthResponse } from "../api/admin";
import { getMe, type UserRead } from "../api/auth";
import { getDashboardSummary, type DashboardSummary } from "../api/dashboard";
import { listProjects, type Project } from "../api/projects";
import "../styles/admin.css";

const defaultSummary: DashboardSummary = {
  project_count: 0,
  completed_count: 0,
  running_count: 0,
  average_score: 0,
  high_risk_count: 0
};

const agentModules = [
  {
    name: "PDF文档解析 Agent",
    skill: "skills/pdf_parser",
    status: "可用",
    desc: "OCR识别、全文抽取、表格解析和关键字段结构化。"
  },
  {
    name: "资质匹配打分 Agent",
    skill: "skills/qualification_matcher",
    status: "可用",
    desc: "核验硬性门槛、材料缺失项和加分机会。"
  },
  {
    name: "投标风险审查 Agent",
    skill: "skills/risk_reviewer",
    status: "可用",
    desc: "识别废标、成本、交付和商务风险。"
  },
  {
    name: "投标方案生成 Agent",
    skill: "skills/proposal_writer",
    status: "可用",
    desc: "生成商务标、技术标大纲和Markdown初稿。"
  }
];

const opsChecks = [
  "前后端接口已接入JWT认证",
  "上传目录和导出目录会自动创建",
  "Router按顺序调度四个独立Skill Agent",
  "分析结果会落库并可再次查看",
  "Docker部署文件已准备完成"
];

function statusCount(projects: Project[], status: string) {
  return projects.filter((project) => project.status === status).length;
}

export function AdminPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserRead | null>(null);
  const [summary, setSummary] = useState<DashboardSummary>(defaultSummary);
  const [projects, setProjects] = useState<Project[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAdminData();
  }, []);

  async function loadAdminData() {
    setLoading(true);
    setError("");
    try {
      const [me, dashboard, projectData, healthData] = await Promise.all([
        getMe(),
        getDashboardSummary().catch(() => defaultSummary),
        listProjects().catch(() => []),
        getSystemHealth().catch(() => ({ status: "unreachable" }))
      ]);
      setUser(me);
      setSummary({ ...defaultSummary, ...dashboard });
      setProjects(projectData);
      setHealth(healthData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "管理后台数据加载失败");
    } finally {
      setLoading(false);
    }
  }

  const projectStatus = useMemo(
    () => [
      { label: "草稿", value: statusCount(projects, "draft") },
      { label: "已上传", value: statusCount(projects, "uploaded") },
      { label: "分析中", value: statusCount(projects, "running") },
      { label: "已完成", value: statusCount(projects, "completed") },
      { label: "失败", value: statusCount(projects, "failed") }
    ],
    [projects]
  );

  return (
    <main className="admin-page">
      <header className="admin-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="admin-eyebrow">系统管理</p>
          <h1>管理后台</h1>
          <p>查看服务状态、当前用户、项目分布和Agent模块可用性。</p>
        </div>
        <button className="admin-refresh" onClick={loadAdminData} disabled={loading}>
          <RefreshCw size={18} className={loading ? "spin" : ""} />
          刷新
        </button>
      </header>

      {error && <div className="admin-alert">{error}</div>}

      <section className="admin-metrics">
        <article>
          <FileStack size={22} />
          <span>项目总数</span>
          <strong>{summary.project_count}</strong>
        </article>
        <article>
          <CheckCircle2 size={22} />
          <span>已完成</span>
          <strong>{summary.completed_count}</strong>
        </article>
        <article>
          <Activity size={22} />
          <span>分析中</span>
          <strong>{summary.running_count}</strong>
        </article>
        <article>
          <ShieldCheck size={22} />
          <span>高风险</span>
          <strong>{summary.high_risk_count ?? 0}</strong>
        </article>
      </section>

      <section className="admin-layout">
        <aside className="admin-side">
          <div className="admin-card user-card">
            <div className="admin-card-title">
              <Users size={21} />
              <h2>当前用户</h2>
            </div>
            <dl>
              <dt>用户名</dt>
              <dd>{user?.username || "-"}</dd>
              <dt>邮箱</dt>
              <dd>{user?.email || "-"}</dd>
              <dt>角色</dt>
              <dd>
                <span className="role-pill">{user?.role || "user"}</span>
              </dd>
              <dt>状态</dt>
              <dd>{user?.status || "-"}</dd>
            </dl>
          </div>

          <div className="admin-card health-card">
            <div className="admin-card-title">
              <Server size={21} />
              <h2>服务健康</h2>
            </div>
            <div className={`health-state ${health?.status === "unreachable" ? "bad" : "good"}`}>
              <Database size={18} />
              <strong>{String(health?.status || "未知")}</strong>
            </div>
            <pre>{JSON.stringify(health || {}, null, 2)}</pre>
          </div>

          <div className="admin-card security-card">
            <div className="admin-card-title">
              <Lock size={21} />
              <h2>安全配置</h2>
            </div>
            <div className="security-row">
              <KeyRound size={18} />
              <span>JWT认证</span>
              <strong>开启</strong>
            </div>
            <div className="security-row">
              <Lock size={18} />
              <span>自动刷新令牌</span>
              <strong>开启</strong>
            </div>
          </div>
        </aside>

        <section className="admin-main">
          <div className="admin-card">
            <div className="admin-card-title">
              <Settings size={21} />
              <h2>项目状态分布</h2>
            </div>
            <div className="status-bars">
              {projectStatus.map((item) => {
                const percent = projects.length > 0 ? Math.round((item.value / projects.length) * 100) : 0;
                return (
                  <div className="status-bar-row" key={item.label}>
                    <span>{item.label}</span>
                    <div className="bar-track">
                      <div style={{ width: `${percent}%` }} />
                    </div>
                    <strong>{item.value}</strong>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="admin-card">
            <div className="admin-card-title">
              <Bot size={21} />
              <h2>Agent模块状态</h2>
            </div>
            <div className="agent-admin-grid">
              {agentModules.map((agent) => (
                <article className="agent-admin-card" key={agent.name}>
                  <div>
                    <h3>{agent.name}</h3>
                    <span>{agent.skill}</span>
                  </div>
                  <p>{agent.desc}</p>
                  <strong>{agent.status}</strong>
                </article>
              ))}
            </div>
          </div>

          <div className="admin-card">
            <div className="admin-card-title">
              <ClipboardIcon />
              <h2>部署检查项</h2>
            </div>
            <ul className="ops-list">
              {opsChecks.map((item) => (
                <li key={item}>
                  <CheckCircle2 size={18} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </section>
    </main>
  );
}

function ClipboardIcon() {
  return <Settings size={21} />;
}
