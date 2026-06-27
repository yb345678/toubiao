import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { getMe, login } from "../api/auth";
import { setAuthTokens, setCachedUser } from "../store/authStore";
import "../styles/auth.css";

export function LoginPage() {
  const navigate = useNavigate();
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
      setAuthTokens(token.access_token, token.refresh_token);
      const user = await getMe();
      setCachedUser(user);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-hero">
        <div className="brand-mark">
          <Bot size={30} />
        </div>
        <p className="eyebrow">AI 招投标多智能体系统</p>
        <h1>上传招标文件，一键完成投标研判。</h1>
        <p className="hero-copy">
          登录后创建投标项目，上传招标 PDF 与企业资质台账，系统将自动调度
          PDF 解析、资质匹配、风险审查和投标方案生成四个 Agent。
        </p>
        <div className="hero-points">
          <span><ShieldCheck size={16} /> JWT 安全登录</span>
          <span><ShieldCheck size={16} /> 多 Agent 自动流转</span>
          <span><ShieldCheck size={16} /> 本地化 Docker 部署</span>
        </div>
      </section>

      <section className="auth-card" aria-label="登录表单">
        <div className="card-heading">
          <h2>登录系统</h2>
          <p>使用企业账号进入投标分析工作台。</p>
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
            {loading ? "登录中..." : "登录"}
          </button>
        </form>

        <p className="switch-link">
          还没有账号？ <Link to="/register">创建账号</Link>
        </p>
      </section>
    </main>
  );
}
