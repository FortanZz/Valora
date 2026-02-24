import ListingCard from "./ListingCard";
import C from "../constants/colors";

export default function ListingsGrid({ listings, title, subtitle, onView }) {
  return (
    <section style={{ maxWidth: 1240, margin: "0 auto", padding: "60px 24px" }}>
      <h2 className="section-title" style={{ marginBottom: 8 }}>{title}</h2>
      <p style={{ color: C.warmGray, marginBottom: 36 }}>
        {subtitle || `${listings.length} propert${listings.length === 1 ? "y" : "ies"} found`}
      </p>
      {listings.length === 0 ? (
        <div style={{ textAlign: "center", padding: "80px 20px", color: C.warmGray }}>
          <p style={{ fontSize: 18 }}>No properties match your search. Try different filters.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24 }}>
          {listings.map((l, i) => (
            <div key={l.id} className="fade-up" style={{ animationDelay: `${i * 0.05}s` }}>
              <ListingCard listing={l} onView={onView} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}