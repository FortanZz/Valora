import { useState } from "react";
import ValoraLogo from "../components/ValoraLogo";
import ListingsGrid from "../components/ListingsGrid";
import C from "../constants/colors";

function HeroSection({ onSearch }) {
  const [q,           setQ]           = useState("");
  const [listingType, setListingType] = useState("buy");

  return (
    <section style={{
      background: `linear-gradient(135deg, ${C.forest} 0%, ${C.forestMid} 60%, ${C.forestLight} 100%)`,
      minHeight: 560, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "80px 24px", position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", top: -80, right: -80, width: 400, height: 400, borderRadius: "50%", background: "rgba(255,255,255,0.04)" }} />
      <div style={{ position: "absolute", bottom: -120, left: -60, width: 300, height: 300, borderRadius: "50%", background: "rgba(255,255,255,0.03)" }} />

      <div className="fade-up" style={{ textAlign: "center", maxWidth: 720, position: "relative" }}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
          <ValoraLogo size={64} />
        </div>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(36px,6vw,68px)", fontWeight: 700, color: C.white, lineHeight: 1.1, marginBottom: 16 }}>
          Find Your<br /><span style={{ color: C.accent }}>Perfect Space.</span>
        </h1>
        <p style={{ fontSize: 18, color: "rgba(255,255,255,0.8)", marginBottom: 40 }}>
          Buy, rent, or list homes, apartments, offices and land across North Macedonia.
        </p>

        <div style={{ background: C.white, borderRadius: 14, padding: 8, display: "flex", gap: 8, flexWrap: "wrap", boxShadow: "0 8px 40px rgba(0,0,0,0.25)", maxWidth: 660, margin: "0 auto" }}>
          <select value={listingType} onChange={e => setListingType(e.target.value)} style={{
            border: "none", background: C.cream, borderRadius: 8, padding: "10px 14px",
            fontWeight: 600, fontSize: 14, color: C.charcoal, cursor: "pointer", outline: "none",
          }}>
            <option value="buy">Buy</option>
            <option value="rent">Rent</option>
          </select>
          <input
            style={{ flex: 1, border: "none", outline: "none", fontSize: 15, padding: "10px 12px", minWidth: 140 }}
            placeholder="Search by city or property type..."
            value={q} onChange={e => setQ(e.target.value)}
            onKeyDown={e => e.key === "Enter" && onSearch(q, listingType)}
          />
          <button className="btn-primary" style={{ borderRadius: 8 }} onClick={() => onSearch(q, listingType)}>
            Search
          </button>
        </div>

        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 24, flexWrap: "wrap" }}>
          {["Houses", "Apartments", "Offices", "Land"].map(tag => (
            <span key={tag} onClick={() => onSearch(tag.toLowerCase(), listingType)} style={{
              background: "rgba(255,255,255,0.15)", color: C.white, padding: "6px 18px",
              borderRadius: 20, fontSize: 13, cursor: "pointer", backdropFilter: "blur(4px)",
            }}>
              {tag}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function StatsBanner() {
  const stats = [
    { n: "1,200+", l: "Active Listings" },
    { n: "850+",   l: "Happy Clients" },
    { n: "15",     l: "Cities Covered" },
    { n: "48M+",  l: "Property Value Sold" },
  ];
  return (
    <section style={{ background: C.forest, padding: "48px 24px" }}>
      <div style={{ maxWidth: 1000, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 32, textAlign: "center" }}>
        {stats.map(s => (
          <div key={s.l}>
            <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 36, fontWeight: 700, color: C.accent }}>{s.n}</div>
            <div style={{ color: "rgba(255,255,255,0.75)", fontSize: 14, marginTop: 4 }}>{s.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function HomePage({ listings, onSearch, onView }) {
  return (
    <div className="fade-in">
      <HeroSection onSearch={onSearch} />
      <StatsBanner />
      <ListingsGrid listings={listings.slice(0, 6)} title="Featured Listings" subtitle="Handpicked properties across North Macedonia" onView={onView} />
    </div>
  );
}