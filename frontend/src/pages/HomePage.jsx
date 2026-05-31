import { useState } from "react";
import ValoraLogo from "../components/ValoraLogo";
import ListingsGrid from "../components/ListingsGrid";
import LISTINGS from "../data/listings";

function HeroSection({ onSearch }) {
  const [q, setQ] = useState("");
  const [listingType, setListingType] = useState("buy");

  function handlePointerMove(event) {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    event.currentTarget.style.setProperty("--mx", `${x}%`);
    event.currentTarget.style.setProperty("--my", `${y}%`);
  }

  function submitSearch() {
    onSearch(q, listingType);
  }

  return (
    <section className="hero-section" onMouseMove={handlePointerMove}>
      <div className="hero-motion-grid" />
      <div className="hero-flow-lines" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>

      <div className="hero-content">
        <div className="hero-copy fade-up">
          <div className="hero-kicker">
            <ValoraLogo size={28} />
            Live property intelligence for North Macedonia
          </div>

          <h1 className="hero-title">
            Find the space that fits your <span>next chapter.</span>
          </h1>

          <p className="hero-subtitle">
            Search polished homes, apartments, offices, and land with a faster,
            more visual way to compare the market.
          </p>

          <div className="hero-search">
            <select
              className="hero-select"
              value={listingType}
              onChange={event => setListingType(event.target.value)}
              aria-label="Listing type"
            >
              <option value="buy">Buy</option>
              <option value="rent">Rent</option>
            </select>
            <input
              className="hero-input"
              placeholder="Search city, neighborhood, or property..."
              value={q}
              onChange={event => setQ(event.target.value)}
              onKeyDown={event => event.key === "Enter" && submitSearch()}
            />
            <button className="btn-primary" onClick={submitSearch}>
              Search
            </button>
          </div>

          <div className="quick-tags">
            {["Skopje", "Ohrid", "Apartments", "Offices", "Land"].map(tag => (
              <button
                key={tag}
                className="quick-tag"
                onClick={() => onSearch(tag.toLowerCase(), listingType)}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        <div className="hero-market-panel" aria-hidden="true">
          <div className="market-card featured">
            <div className="market-label">Featured match</div>
            <div className="market-title">Karpos Luxury Apartment</div>
            <div className="market-row">
              <span className="market-price">EUR 92k</span>
              <span className="market-meta">3 beds / 110 sqm</span>
            </div>
          </div>

          <div className="market-card">
            <div className="market-row">
              <div>
                <div className="market-label">Demand pulse</div>
                <div className="market-title">Skopje Center</div>
              </div>
              <span className="market-price">+18%</span>
            </div>
            <div className="market-bar" />
          </div>

          <div className="market-card">
            <div className="market-row">
              <div>
                <div className="market-label">Fresh listings</div>
                <div className="market-title">42 this week</div>
              </div>
              <span className="market-meta">Updated live</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function StatsBanner() {
  const stats = [
    { n: "1,200+", l: "Active Listings" },
    { n: "850+", l: "Happy Clients" },
    { n: "15", l: "Cities Covered" },
    { n: "48M+", l: "Property Value Sold" },
  ];

  return (
    <section className="stats-band">
      <div className="stats-grid">
        {stats.map(stat => (
          <div key={stat.l} className="stat-item">
            <div className="stat-number">{stat.n}</div>
            <div className="stat-label">{stat.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function HomePage({ listings, onSearch, onView }) {
  const featuredListings = listings.length ? listings.slice(0, 6) : LISTINGS.slice(0, 6);

  return (
    <div className="fade-in">
      <HeroSection onSearch={onSearch} />
      <StatsBanner />
      <ListingsGrid
        listings={featuredListings}
        title="Featured Listings"
        subtitle="Handpicked properties across North Macedonia"
        onView={onView}
      />
    </div>
  );
}
