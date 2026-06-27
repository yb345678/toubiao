import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BarChart3,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  FileSearch,
  Filter,
  RefreshCw,
  Search
} from "lucide-react";
import { listProjects, type Project } from "../api/projects";
import "../styles/history.css";

type StatusFilter = "all" | "draft" | "uploaded" | "running" | "completed" | "failed";

const statusOptions: StatusFilter[] = ["all", "draft", "uploaded", "running", "completed", "failed"];

const statusLabels: Record<StatusFilter, string> = {
  all: "全部状态",
  draft: "草稿",
  uploaded: "已上传",
  running: "分析中",
  completed: "已完成",
  failed: "失败"
};

function formatDate(value: string) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function statusClass(status: string) {
  if (["completed", "failed", "running", "uploaded", "draft"].includes(status)) {
    return status;
  }
  return "draft";
}

export function HistoryPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState<StatusFilter>("all");

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    setLoading(true);
    setError("");
    try {
      const data = await listProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "历史记录加载失败");
    } finally {
      setLoading(false);
    }
  }

  const filteredProjects = useMemo(() => {
    const text = keyword.trim().toLowerCase();
    return projects
      .filter((project) => {
        if (status !== "all" && project.status !== status) return false;
        if (!text) return true;
        return [project.name, project.tender_name, project.tender_company, project.latest_recommendation]
          .filter(Boolean)
          .some((item) => String(item).toLowerCase().includes(text));
      })
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }, [projects, keyword, status]);

  const stats = useMemo(
    () => ({
      total: projects.length,
      completed: projects.filter((project) => project.status === "completed").length,
      running: projects.filter((project) => project.status === "running").length,
      averageScore:
        projects.filter((project) => typeof project.latest_score === "number").length > 0
          ? Math.round(
              projects.reduce((sum, project) => sum + (project.latest_score || 0), 0) /
                projects.filter((project) => typeof project.latest_score === "number").length
            )
          : 0
    }),
    [projects]
  );

  return (
    <main className="history-page">
      <header className="history-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="history-eyebrow">历史记录</p>
          <h1>项目分析历史</h1>
          <p>查看已上传项目、分析状态、匹配得分和投标建议。</p>
        </div>
      </header>

      <section className="history-stats">
        <article>
          <CalendarClock size={22} />
          <span>项目总数</span>
          <strong>{stats.total}</strong>
        </article>
        <article>
          <CheckCircle2 size={22} />
          <span>已完成</span>
          <strong>{stats.completed}</strong>
        </article>
        <article>
          <FileSearch size={22} />
          <span>分析中</span>
          <strong>{stats.running}</strong>
        </article>
        <article>
          <BarChart3 size={22} />
          <span>平均得分</span>
          <strong>{stats.averageScore}</strong>
        </article>
      </section>

      <section className="history-toolbar">
        <label className="search-box">
          <Search size={18} />
          <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索项目、招标单位或结论" />
        </label>
        <label className="filter-box">
          <Filter size={18} />
          <select value={status} onChange={(event) => setStatus(event.target.value as StatusFilter)}>
            {statusOptions.map((item) => (
              <option value={item} key={item}>
                {statusLabels[item]}
              </option>
            ))}
          </select>
        </label>
        <button onClick={loadHistory} disabled={loading}>
          <RefreshCw size={18} className={loading ? "spin" : ""} />
          刷新
        </button>
      </section>

      {error && <div className="history-alert">{error}</div>}

      <section className="history-table-panel">
        <div className="history-table">
          <div className="history-row header">
            <span>项目</span>
            <span>状态</span>
            <span>得分</span>
            <span>投标建议</span>
            <span>创建时间</span>
            <span>操作</span>
          </div>

          {filteredProjects.length === 0 ? (
            <div className="history-empty">
              <ClipboardList size={22} />
              <span>{loading ? "正在加载历史记录..." : "暂无匹配记录"}</span>
            </div>
          ) : (
            filteredProjects.map((project) => (
              <div className="history-row" key={project.id}>
                <div className="project-cell">
                  <strong>{project.name}</strong>
                  <span>{project.tender_company || project.tender_name || project.id}</span>
                </div>
                <span className={`history-status ${statusClass(project.status)}`}>{statusLabels[project.status as StatusFilter] || project.status}</span>
                <span>{project.latest_score ?? "-"}</span>
                <span>{project.latest_recommendation || "-"}</span>
                <span>{formatDate(project.created_at)}</span>
                <div className="history-actions">
                  <button onClick={() => navigate("/analysis")}>分析</button>
                  <button onClick={() => navigate("/risks")}>风险</button>
                  <button onClick={() => navigate("/proposal")}>方案</button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}
