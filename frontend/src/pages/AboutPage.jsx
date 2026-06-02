import ValoraLogo from "../components/ValoraLogo";

const TEAM = [
  { name: "Zeqirija Osmani", initial: "Z" },
  { name: "Fortan Zaimi", initial: "F" },
  { name: "Dren Bajrami", initial: "D" },
];

const VALUES = [
  { title: "Clear Listings", desc: "Prices, contact details, and property facts stay easy to scan so every search starts with useful information." },
  { title: "Direct Access", desc: "Valora keeps buyers, renters, and sellers close to the next step instead of burying the action." },
  { title: "Fast Discovery", desc: "Simple filters and focused cards help people compare homes, offices, apartments, and land quickly." },
  { title: "Practical Design", desc: "Every page is shaped around real property decisions, from browsing to opening a listing." },
];

export default function AboutPage({ onBrowse }) {
  return (
    <div className="fade-in">
      <section className="about-hero">
        <div className="about-hero-inner">
          <ValoraLogo size={64} />
          <h1>About Valora</h1>
          <p>
            A focused real estate platform for comparing spaces clearly,
            contacting sellers faster, and moving from search to decision.
          </p>
        </div>
      </section>

      <section className="about-section">
        <div className="about-mission-grid two-col">
          <div>
            <h2 className="section-title">Our Mission</h2>
            <p>
              Valora was built around a simple idea: property search should feel
              direct, visual, and transparent. We bring homes, apartments,
              offices, and land into one place so people can compare real
              opportunities without extra friction.
            </p>
            <p>
              The experience is designed for buyers, renters, sellers, and
              investors who want the important details first and a clear path to
              the next conversation.
            </p>
          </div>

          <div className="about-mission-panel">
            <span>Built for clarity</span>
            <strong>Search less. Compare better.</strong>
            <p>
              A calm interface, useful filters, and listing cards that surface
              the facts people actually need.
            </p>
            <div className="about-mission-stats">
              <div>
                <strong>4</strong>
                <span>property types</span>
              </div>
              <div>
                <strong>1</strong>
                <span>focused platform</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="about-values-section">
        <div className="about-section-inner">
          <h2 className="section-title">Our Values</h2>
          <div className="about-values-grid">
            {VALUES.map(value => (
              <div key={value.title} className="card about-value-card">
                <div>{value.title}</div>
                <p>{value.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="about-team-section">
        <div className="about-section-inner">
          <h2 className="section-title">Meet the Team</h2>
          <div className="about-team-grid">
            {TEAM.map(member => (
              <div key={member.name} className="card about-team-card">
                <div className="about-team-initial">{member.initial}</div>
                <div className="about-team-name">{member.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="about-cta">
        <h2>Ready to find your space?</h2>
        <p>Browse listings or list your property today.</p>
        <button className="btn-primary about-cta-button" onClick={onBrowse}>
          Browse Listings
        </button>
      </section>
    </div>
  );
}
