import ValoraLogo from "./ValoraLogo";
import C from "../constants/colors";

const COLS = [
  { title: "Explore",  links: [{ label: "Buy",     page: "buy" }, { label: "Rent", page: "rent" }, { label: "Sell", page: "sell" }] },
  { title: "Company",  links: [{ label: "About Us", page: "about" }, { label: "Contact", page: "contact" }] },
  { title: "Connect",  links: [{ label: "Instagram", page: null }, { label: "Twitter", page: null }, { label: "LinkedIn", page: null }] },
];

export default function Footer({ onNav }) {
  return (
    <footer style={{ background: C.charcoal, color: "rgba(255,255,255,0.7)", padding: "52px 24px 28px" }}>
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 40, marginBottom: 48 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
              <ValoraLogo size={36} />
              <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: C.white }}>Valora</span>
            </div>
            <p style={{ fontSize: 14, lineHeight: 1.8, maxWidth: 280 }}>
              Your trusted platform for buying, renting, and selling real estate. Find your perfect space.
            </p>
          </div>
          {COLS.map(col => (
            <div key={col.title}>
              <div style={{ fontWeight: 700, color: C.white, marginBottom: 14, fontSize: 15 }}>{col.title}</div>
              {col.links.map(lk => (
                <div key={lk.label} style={{ marginBottom: 10 }}>
                  <button onClick={() => lk.page && onNav(lk.page)} style={{
                    background: "none", border: "none", color: "rgba(255,255,255,0.6)",
                    cursor: lk.page ? "pointer" : "default", fontSize: 14, padding: 0,
                    transition: "color 0.15s",
                  }}
                    onMouseEnter={e => lk.page && (e.target.style.color = C.accent)}
                    onMouseLeave={e => (e.target.style.color = "rgba(255,255,255,0.6)")}
                  >
                    {lk.label}
                  </button>
                </div>
              ))}
            </div>
          ))}
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: 24, display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
          <p style={{ fontSize: 13 }}>© {new Date().getFullYear()} Valora. All rights reserved.</p>
          <p style={{ fontSize: 13 }}>Made with ❤️ for real estate, reimagined.</p>
        </div>
      </div>
    </footer>
  );
}