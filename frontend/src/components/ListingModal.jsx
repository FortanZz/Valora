import C from "../constants/colors";

export default function ListingModal({ listing, onClose }) {
  const isRent = listing.listing === "rent";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()} style={{ maxWidth: 700 }}>
        <button onClick={onClose} style={{
          position: "absolute", top: 16, right: 20,
          background: "none", border: "none", fontSize: 24, cursor: "pointer", color: C.warmGray,
        }}>x</button>

        <img src={listing.img} alt={listing.name}
          style={{ width: "100%", height: 280, objectFit: "cover", borderRadius: 10, marginBottom: 24 }} />

        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <span className={`tag ${isRent ? "tag-rent" : "tag-buy"}`}>{listing.listing.toUpperCase()}</span>
          <span className="tag tag-neutral" style={{ background: C.sand }}>{listing.type.toUpperCase()}</span>
        </div>

        <h2 className="section-title" style={{ fontSize: 26, marginBottom: 6 }}>{listing.name}</h2>
        <p style={{ color: C.warmGray, marginBottom: 20 }}>{listing.location}</p>

        <div style={{ fontSize: 28, fontWeight: 800, color: C.forest, marginBottom: 20 }}>
          {isRent ? `€${listing.price.toLocaleString()}/month` : `€${listing.price.toLocaleString()}`}
        </div>

        {(listing.beds > 0 || listing.sqft > 0) && (
          <div style={{ display: "flex", gap: 24, marginBottom: 20, padding: "16px 20px", background: C.cream, borderRadius: 10 }}>
            {listing.beds  > 0 && (
              <div>
                <div style={{ fontSize: 20, fontWeight: 700 }}>{listing.beds}</div>
                <div style={{ fontSize: 12, color: C.warmGray }}>Bedrooms</div>
              </div>
            )}
            {listing.baths > 0 && (
              <div>
                <div style={{ fontSize: 20, fontWeight: 700 }}>{listing.baths}</div>
                <div style={{ fontSize: 12, color: C.warmGray }}>Bathrooms</div>
              </div>
            )}
            {listing.sqft  > 0 && (
              <div>
                <div style={{ fontSize: 20, fontWeight: 700 }}>{listing.sqft.toLocaleString()}</div>
                <div style={{ fontSize: 12, color: C.warmGray }}>m²</div>
              </div>
            )}
          </div>
        )}

        {listing.description && (
          <p style={{ color: C.charcoal, lineHeight: 1.8, fontSize: 15, marginBottom: 20 }}>{listing.description}</p>
        )}

        <div style={{ padding: 20, background: C.cream, borderRadius: 10 }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Contact Seller</div>
          <div style={{ fontSize: 15 }}>{listing.seller}</div>
          <div style={{ color: C.forest, fontWeight: 600, marginTop: 4, fontSize: 15 }}>{listing.phone}</div>
          {listing.sourceUrl && (
            <button className="btn-outline" style={{ marginTop: 14, width: "100%" }}
              onClick={() => window.open(listing.sourceUrl, "_blank", "noopener,noreferrer")}>
              Open Source Listing
            </button>
          )}
          <button className="btn-primary" style={{ marginTop: 14, width: "100%" }}
            onClick={() => window.open(`tel:${listing.phone}`)}>
            Call Seller
          </button>
        </div>
      </div>
    </div>
  );
}
