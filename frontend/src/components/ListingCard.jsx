import C from "../constants/colors";

export default function ListingCard({ listing, onView }) {
  const isRent = listing.listing === "rent";

  return (
    <div className="card listing-card" onClick={() => onView(listing)}>
      <div style={{ position: "relative", height: 200, overflow: "hidden" }}>
        <img
          src={listing.img}
          alt={listing.name}
          className="listing-card-image"
        />
        <div style={{ position: "absolute", top: 12, left: 12, display: "flex", gap: 6 }}>
          <span className={`tag ${isRent ? "tag-rent" : listing.type === "land" ? "tag-land" : "tag-buy"}`}>
            {listing.listing}
          </span>
          <span className="tag tag-neutral" style={{ background: "rgba(255,255,255,0.92)", color: C.charcoal }}>
            {listing.type}
          </span>
        </div>
      </div>

      <div style={{ padding: "18px 20px 20px" }}>
        <div className="listing-card-price">
          {isRent ? `€${listing.price.toLocaleString()}/mo` : `€${listing.price.toLocaleString()}`}
        </div>
        <div style={{ fontSize: 15, fontWeight: 600, marginTop: 4 }}>{listing.name}</div>
        <div style={{ fontSize: 13, color: C.warmGray, marginTop: 2 }}>{listing.location}</div>

        {(listing.beds > 0 || listing.sqft > 0) && (
          <div style={{ display: "flex", gap: 16, marginTop: 12, fontSize: 13, color: C.warmGray }}>
            {listing.beds  > 0 && <span>{listing.beds} Beds</span>}
            {listing.baths > 0 && <span>{listing.baths} Baths</span>}
            {listing.sqft  > 0 && <span>{listing.sqft.toLocaleString()} m²</span>}
          </div>
        )}

        <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${C.sand}`, fontSize: 13, color: C.warmGray }}>
          {listing.seller}
        </div>
      </div>
    </div>
  );
}
