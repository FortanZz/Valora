import { useEffect, useRef, useState } from "react";
import ValoraLogo from "../components/ValoraLogo";
import ListingsGrid from "../components/ListingsGrid";
import LISTINGS from "../data/listings";

function HeroSection({ onSearch }) {
  const [q, setQ] = useState("");
  const [listingType, setListingType] = useState("buy");
  const heroRef = useRef(null);
  const pointerRef = useRef({
    currentX: 50,
    currentY: 42,
    targetX: 50,
    targetY: 42,
  });

  useEffect(() => {
    let frameId;

    function animatePointerGlow() {
      const pointer = pointerRef.current;
      pointer.currentX += (pointer.targetX - pointer.currentX) * 0.08;
      pointer.currentY += (pointer.targetY - pointer.currentY) * 0.08;

      if (heroRef.current) {
        heroRef.current.style.setProperty("--mx", `${pointer.currentX}%`);
        heroRef.current.style.setProperty("--my", `${pointer.currentY}%`);
      }

      frameId = requestAnimationFrame(animatePointerGlow);
    }

    frameId = requestAnimationFrame(animatePointerGlow);
    return () => cancelAnimationFrame(frameId);
  }, []);

  function handlePointerMove(event) {
    const rect = event.currentTarget.getBoundingClientRect();
    pointerRef.current.targetX = ((event.clientX - rect.left) / rect.width) * 100;
    pointerRef.current.targetY = ((event.clientY - rect.top) / rect.height) * 100;
  }

  function resetPointerGlow() {
    pointerRef.current.targetX = 50;
    pointerRef.current.targetY = 42;
  }

  function submitSearch() {
    onSearch(q, listingType);
  }

  return (
    <section
      ref={heroRef}
      className="hero-section"
      onMouseMove={handlePointerMove}
      onMouseLeave={resetPointerGlow}
    >
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
            Live property intelligence for modern real estate
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
            {["Lakewood", "Northgate", "Apartments", "Offices", "Land"].map(tag => (
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
            <div className="market-title">Lakewood Glass House</div>
            <div className="market-row">
              <span className="market-price">EUR 685k</span>
              <span className="market-meta">4 beds / 340 sqm</span>
            </div>
          </div>

          <div className="market-card">
            <div className="market-row">
              <div>
                <div className="market-label">Demand pulse</div>
                <div className="market-title">Northgate</div>
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
  const cityCount = new Set(LISTINGS.map(item => item.location.split(",")[0].trim())).size;
  const stats = [
    { n: `${LISTINGS.length}+`, l: "Seeded Listings" },
    { n: `${cityCount}`, l: "Cities Covered" },
    { n: "4", l: "Property Types" },
    { n: "Live", l: "Backend Ready" },
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
        subtitle="Handpicked demo properties across every category"
        onView={onView}
      />
    </div>
  );
}
