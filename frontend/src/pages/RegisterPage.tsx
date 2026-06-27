import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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
      setError(err instanceof Error ? err.message : "注册失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page single">
      <section className="auth-card" aria-label="注册表单">
        <div className="card-heading">
          <h2>创建账号</h2>
          <p>注册后即可创建企业投标分析项目。</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            <span>邮箱</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>
            <span>用户名</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} required />
          </label>
          <label>
            <span>密码</span>
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
          </label>
          {error && <div className="form-error">{error}</div>}
          <button disabled={loading} type="submit">{loading ? "创建中..." : "创建账号"}</button>
        </form>
        <p className="switch-link">
          已有账号？ <Link to="/login">返回登录</Link>
        </p>
      </section>
    </main>
  );
}
