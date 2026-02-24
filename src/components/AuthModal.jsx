import { useState } from "react";
import ValoraLogo from "./ValoraLogo";
import C from "../constants/colors";

export default function AuthModal({ mode, onClose, onSuccess }) {
  const [tab,  setTab]  = useState(mode);
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [err,  setErr]  = useState("");

  function set(k, v) { setForm(p => ({ ...p, [k]: v })); }

  function submit(e) {
    e.preventDefault();
    setErr("");
    if (tab === "register" && !form.name.trim()) { setErr("Name is required."); return; }
    if (!form.email.includes("@"))               { setErr("Enter a valid email."); return; }
    if (form.password.length < 6)                { setErr("Password must be at least 6 characters."); return; }
    onSuccess({ name: form.name || form.email.split("@")[0], email: form.email });
  }

  const TabBtn = ({ id, label }) => (
    <button onClick={() => { setTab(id); setErr(""); }} style={{
      flex: 1, padding: "10px 0", border: "none", background: "none", cursor: "pointer",
      fontWeight: 600, fontSize: 15,
      color: tab === id ? C.forest : C.warmGray,
      borderBottom: tab === id ? `2px solid ${C.forest}` : "2px solid transparent",
      marginBottom: -2, transition: "all 0.2s",
    }}>{label}</button>
  );

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} style={{ position: "absolute", top: 16, right: 20, background: "none", border: "none", fontSize: 24, cursor: "pointer", color: C.warmGray }}>x</button>

        <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
          <ValoraLogo size={52} />
        </div>

        <div style={{ display: "flex", marginBottom: 28, borderBottom: `2px solid ${C.sand}` }}>
          <TabBtn id="login"    label="Sign In" />
          <TabBtn id="register" label="Create Account" />
        </div>

        <form onSubmit={submit}>
          {tab === "register" && (
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Full Name</label>
              <input className="input-field" placeholder="Your name" value={form.name} onChange={e => set("name", e.target.value)} />
            </div>
          )}
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Email</label>
            <input className="input-field" type="email" placeholder="you@email.com" value={form.email} onChange={e => set("email", e.target.value)} />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Password</label>
            <input className="input-field" type="password" placeholder="••••••••" value={form.password} onChange={e => set("password", e.target.value)} />
          </div>
          {err && <p style={{ color: "#c00", fontSize: 13, marginBottom: 12 }}>{err}</p>}
          <button type="submit" className="btn-primary" style={{ width: "100%", padding: 14, fontSize: 16 }}>
            {tab === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <p style={{ textAlign: "center", color: C.warmGray, fontSize: 13, marginTop: 20 }}>
          {tab === "login" ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setTab(tab === "login" ? "register" : "login")} style={{
            background: "none", border: "none", color: C.forest, fontWeight: 600, cursor: "pointer", fontSize: 13,
          }}>
            {tab === "login" ? "Sign up free" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}