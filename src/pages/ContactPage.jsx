import { useState } from "react";
import C from "../constants/colors";

const INFO = [
  { icon: "📍", label: "Address", value: "1400 Valora Blvd, Suite 300\nAustin, TX 78701" },
  { icon: "📞", label: "Phone",   value: "+1 (512) 000-9999" },
  { icon: "✉️", label: "Email",   value: "hello@valora.app" },
  { icon: "🕐", label: "Hours",   value: "Mon–Fri: 9am–6pm CST\nSat: 10am–2pm CST" },
];

export default function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sent, setSent] = useState(false);
  const [err,  setErr]  = useState("");

  function set(k, v) { setForm(p => ({ ...p, [k]: v })); }

  function submit(e) {
    e.preventDefault();
    setErr("");
    if (!form.name.trim())         { setErr("Name is required."); return; }
    if (!form.email.includes("@")) { setErr("Enter a valid email."); return; }
    if (!form.message.trim())      { setErr("Message is required."); return; }
    setSent(true);
  }

  return (
    <div className="fade-in">
      <section style={{ background: `linear-gradient(135deg, ${C.forest}, ${C.forestMid})`, padding: "72px 24px", textAlign: "center" }}>
        <h1 style={{ fontFamily: "'Playfair Display',serif", fontSize: "clamp(32px,5vw,52px)", fontWeight: 700, color: C.white, marginBottom: 16 }}>
          Get In Touch
        </h1>
        <p style={{ color: "rgba(255,255,255,0.8)", fontSize: 17, maxWidth: 500, margin: "0 auto" }}>
          We'd love to hear from you. Our team responds within 24 hours.
        </p>
      </section>

      <section style={{ maxWidth: 1020, margin: "0 auto", padding: "72px 24px", display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 60, alignItems: "start" }} className="two-col">
        <div>
          <h2 className="section-title" style={{ fontSize: 28, marginBottom: 28 }}>Contact Info</h2>
          {INFO.map(item => (
            <div key={item.label} style={{ display: "flex", gap: 16, marginBottom: 28, alignItems: "flex-start" }}>
              <div style={{ width: 46, height: 46, background: C.cream, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0 }}>
                {item.icon}
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 3 }}>{item.label}</div>
                <div style={{ color: C.warmGray, fontSize: 14, lineHeight: 1.7, whiteSpace: "pre-line" }}>{item.value}</div>
              </div>
            </div>
          ))}
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 14 }}>Follow Us</div>
            <div style={{ display: "flex", gap: 10 }}>
              {["Instagram", "Twitter", "LinkedIn"].map(s => (
                <span key={s} style={{ background: C.cream, padding: "8px 14px", borderRadius: 8, fontSize: 13, fontWeight: 600, color: C.forest, cursor: "pointer" }}>{s}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: 40 }}>
          {sent ? (
            <div style={{ textAlign: "center", padding: "40px 0" }}>
              <div style={{ fontSize: 60, marginBottom: 16 }}>✅</div>
              <h3 style={{ fontFamily: "'Playfair Display',serif", fontSize: 24, marginBottom: 10 }}>Message Sent!</h3>
              <p style={{ color: C.warmGray }}>Thanks for reaching out. We'll get back to you within 24 hours.</p>
              <button className="btn-primary" style={{ marginTop: 24 }}
                onClick={() => { setSent(false); setForm({ name: "", email: "", subject: "", message: "" }); }}>
                Send Another
              </button>
            </div>
          ) : (
            <form onSubmit={submit}>
              <h3 style={{ fontFamily: "'Playfair Display',serif", fontSize: 22, marginBottom: 28 }}>Send a Message</h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
                <div>
                  <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Name <span style={{ color: "#c00" }}>*</span></label>
                  <input className="input-field" placeholder="Your name" value={form.name} onChange={e => set("name", e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Email <span style={{ color: "#c00" }}>*</span></label>
                  <input className="input-field" type="email" placeholder="you@email.com" value={form.email} onChange={e => set("email", e.target.value)} />
                </div>
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Subject</label>
                <input className="input-field" placeholder="How can we help?" value={form.subject} onChange={e => set("subject", e.target.value)} />
              </div>
              <div style={{ marginBottom: 22 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>Message <span style={{ color: "#c00" }}>*</span></label>
                <textarea className="input-field" rows={5} placeholder="Write your message here..." value={form.message} onChange={e => set("message", e.target.value)} style={{ resize: "vertical" }} />
              </div>
              {err && <p style={{ color: "#c00", fontSize: 13, marginBottom: 14 }}>⚠️ {err}</p>}
              <button type="submit" className="btn-primary" style={{ width: "100%", padding: 14, fontSize: 16 }}>
                📨 Send Message
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}