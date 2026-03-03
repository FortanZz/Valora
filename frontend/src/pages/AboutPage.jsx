import ValoraLogo from "../components/ValoraLogo";
import C from "../constants/colors";

const TEAM = [
  { name: "Arben Bajrami",   role: "CEO & Co-Founder",   initial: "A" },
  { name: "Fjolla Berisha",  role: "CTO & Co-Founder",   initial: "F" },
  { name: "Driton Hoxha",    role: "Head of Design",     initial: "D" },
  { name: "Arta Mustafa",    role: "Head of Operations", initial: "A" },
];

const VALUES = [
  { title: "Transparency", desc: "Every listing shows real prices, real contact info, and real details with no hidden fees." },
  { title: "Trust",        desc: "We verify sellers and maintain community standards across all listings on our platform." },
  { title: "Speed",        desc: "From search to seller contact in seconds. Modern real estate at the speed of life." },
  { title: "Inclusivity",  desc: "From first-time renters to seasoned investors — Valora is built for everyone in North Macedonia." },
];

export default function AboutPage() {
  return (
    <div className="fade-in">
      <section style={{ background: `linear-gradient(135deg, ${C.forest}, ${C.forestMid})`, padding: "80px 24px", textAlign: "center" }}>
        <ValoraLogo size={64} />
        <h1 style={{ fontFamily: "'Playfair Display',serif", fontSize: "clamp(32px,5vw,56px)", fontWeight: 700, color: C.white, marginTop: 20, marginBottom: 16 }}>
          About Valora
        </h1>
        <p style={{ color: "rgba(255,255,255,0.8)", fontSize: 18, maxWidth: 600, margin: "0 auto" }}>
          Reimagining real estate for everyone in North Macedonia — buyers, renters, sellers, and investors.
        </p>
      </section>

      <section style={{ maxWidth: 960, margin: "0 auto", padding: "72px 24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center" }} className="two-col">
          <div>
            <h2 className="section-title" style={{ marginBottom: 20 }}>Our Mission</h2>
            <p style={{ color: C.warmGray, lineHeight: 1.85, fontSize: 16 }}>
              Valora was built on a simple idea: finding, buying, renting, or selling a property should be transparent, fast, and stress-free. We connect property seekers directly with sellers — no hidden fees, no middlemen.
            </p>
            <p style={{ color: C.warmGray, lineHeight: 1.85, fontSize: 16, marginTop: 16 }}>
              Whether you are searching for a family home, a city apartment, a commercial office, or a plot of land — Valora brings every listing together in one professional platform built for North Macedonia.
            </p>
          </div>
          <div style={{ background: C.cream, borderRadius: 20, padding: 40, textAlign: "center" }}>
            <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 26, fontWeight: 700, color: C.forest, lineHeight: 1.4 }}>
              "Real estate,<br />reimagined."
            </div>
          </div>
        </div>
      </section>

      <section style={{ background: C.cream, padding: "60px 24px" }}>
        <div style={{ maxWidth: 1040, margin: "0 auto" }}>
          <h2 className="section-title" style={{ textAlign: "center", marginBottom: 40 }}>Our Values</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 24 }}>
            {VALUES.map(v => (
              <div key={v.title} className="card" style={{ padding: 28 }}>
                <div style={{ fontWeight: 700, fontSize: 17, marginBottom: 10 }}>{v.title}</div>
                <p style={{ color: C.warmGray, fontSize: 14, lineHeight: 1.75 }}>{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section style={{ maxWidth: 900, margin: "0 auto", padding: "72px 24px" }}>
        <h2 className="section-title" style={{ textAlign: "center", marginBottom: 40 }}>Meet the Team</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 24 }}>
          {TEAM.map(m => (
            <div key={m.name} className="card" style={{ padding: 32, textAlign: "center" }}>
              <div style={{
                width: 60, height: 60, borderRadius: "50%", background: C.forest,
                color: C.white, fontSize: 22, fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center",
                margin: "0 auto 16px",
              }}>
                {m.initial}
              </div>
              <div style={{ fontWeight: 700, fontSize: 16 }}>{m.name}</div>
              <div style={{ color: C.warmGray, fontSize: 13, marginTop: 6 }}>{m.role}</div>
            </div>
          ))}
        </div>
      </section>

      <section style={{ background: C.forest, padding: "60px 24px", textAlign: "center" }}>
        <h2 style={{ fontFamily: "'Playfair Display',serif", fontSize: 32, color: C.white, marginBottom: 16 }}>
          Ready to find your space?
        </h2>
        <p style={{ color: "rgba(255,255,255,0.75)", marginBottom: 28, fontSize: 16 }}>
          Browse listings or list your property today.
        </p>
        <button className="btn-primary" style={{ background: C.accent, color: C.charcoal, fontSize: 16, padding: "14px 36px" }}>
          Browse Listings
        </button>
      </section>
    </div>
  );
}