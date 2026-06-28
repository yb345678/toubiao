import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot, LockKeyhole, Mail, UserRound } from "lucide-react";
import { register } from "../api/auth";
import "../styles/auth.css";

export function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ email, username, password });
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page single">
      <section className="auth-card elevated" aria-label="注册表单">
        <div className="compact-brand">
          <Bot size={24} />
        </div>
        <div className="card-heading">
          <p className="card-kicker">Create Account</p>
          <h2>创建企业账号</h2>
          <p>注册后即可创建投标项目、上传资料并启动多 Agent 分析。</p>
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
            <span>用户名</span>
            <div className="input-wrap">
              <UserRound size={18} />
              <input value={username} onChange={(event) => setUsername(event.target.value)} required />
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
                autoComplete="new-password"
                placeholder="至少 8 位，建议包含大小写与数字"
                required
              />
            </div>
          </label>
          {error && <div className="form-error">{error}</div>}
          <button disabled={loading} type="submit">{loading ? "正在创建..." : "创建账号"}</button>
        </form>
        <p className="switch-link">
          已有账号？ <Link to="/login">返回登录</Link>
        </p>
      </section>
    </main>
  );
}
