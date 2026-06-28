import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  FileSearch,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import { getMe, login } from "../api/auth";
import { setAuthTokens, setCachedUser } from "../store/authStore";
import "../styles/auth.css";

export function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Passw0rd!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const token = await login({ email, password });
      if (typeof token.access_token !== "string" || !token.access_token.trim()) {
        throw new Error("登录接口未返回有效 access_token");
      }
      if (typeof token.refresh_token !== "string" || !token.refresh_token.trim()) {
        throw new Error("登录接口未返回有效 refresh_token");
      }
      setAuthTokens(token.access_token, token.refresh_token);
      const user = await getMe();
      setCachedUser(user);
      navigate(searchParams.get("next") || "/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败，请检查账号或后端服务状态");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-hero">
        <div className="hero-topline">
          <div className="brand-mark">
            <Bot size={30} />
          </div>
          <span className="live-badge">
            <Sparkles size={15} />
            Multi-Agent Bidding Platform
          </span>
        </div>

        <p className="eyebrow">AI 招投标多智能体系统</p>
        <h1>让招标文件自动进入企业投标研判流程</h1>
        <p className="hero-copy">
          上传招标 PDF 与企业资质台账，系统自动完成 PDF 解析、资质匹配、风险审查和投标方案生成，
          为黑客松路演提供一套可演示、可追溯、可导出的企业级工作台。
        </p>

        <div className="hero-metrics" aria-label="平台能力概览">
          <div>
            <strong>4</strong>
            <span>独立 Agent</span>
          </div>
          <div>
            <strong>60s</strong>
            <span>快速研判</span>
          </div>
          <div>
            <strong>100%</strong>
            <span>本地/私有化流程</span>
          </div>
        </div>

        <div className="hero-points">
          <span>
            <ShieldCheck size={16} />
            JWT 安全登录
          </span>
          <span>
            <FileSearch size={16} />
            页码级原文溯源
          </span>
          <span>
            <CheckCircle2 size={16} />
            一键导出报告
          </span>
        </div>
      </section>

      <section className="auth-card" aria-label="登录表单">
        <div className="card-heading">
          <p className="card-kicker">Workspace Login</p>
          <h2>登录工作台</h2>
          <p>使用企业账号进入投标分析控制台。</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            <span>邮箱</span>
            <div className="input-wrap">
              <Mail size={18} />
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                autoComplete="email"
                placeholder="name@company.com"
                required
              />
            </div>
          </label>

          <label>
            <span>密码</span>
            <div className="input-wrap">
              <LockKeyhole size={18} />
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                autoComplete="current-password"
                placeholder="请输入密码"
                required
              />
            </div>
          </label>

          {error && <div className="form-error">{error}</div>}

          <button disabled={loading} type="submit">
            {loading ? "正在登录..." : "进入系统"}
            {!loading && <ArrowRight size={18} />}
          </button>
        </form>

        <p className="switch-link">
          还没有账号？ <Link to="/register">创建企业账号</Link>
        </p>
      </section>
    </main>
  );
}
