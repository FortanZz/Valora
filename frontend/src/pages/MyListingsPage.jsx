import { useEffect, useState } from "react";
import ListingCard from "../components/ListingCard";
import C from "../constants/colors";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api";

function mapApiProperty(property) {
  return {
    id: `api-${property.id}`,
    apiId: property.id,
    listing: property.category === "rent" ? "rent" : "buy",
    type: property.property_type,
    name: property.title,
    location: property.location,
    price: property.price,
    beds: property.num_bedrooms || 0,
    baths: property.num_bathrooms || 0,
    sqft: property.area_sqm || 0,
    seller: property.contact_email,
    phone: property.contact_phone,
    description: property.description || "",
    img: property.image_url || "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&q=80",
  };
}

export default function MyListingsPage({ authToken, onView }) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadMyListings() {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(`${API_BASE}/properties/mine`, {
          headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Unable to load your listings");
        }
        if (active) setListings(data.map(mapApiProperty));
      } catch (err) {
        if (active) setError(err.message || "Unable to load your listings");
      } finally {
        if (active) setLoading(false);
      }
    }

    if (authToken) {
      loadMyListings();
    } else {
      setLoading(false);
      setError("Sign in to view your listings.");
    }

    return () => {
      active = false;
    };
  }, [authToken]);

  async function deleteListing(listing) {
    setDeletingId(listing.apiId);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/properties/${listing.apiId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!response.ok) {
        let message = "Unable to delete listing";
        try {
          const data = await response.json();
          message = data.detail || message;
        } catch (_) {
          message = "Unable to delete listing";
        }
        throw new Error(message);
      }
      setListings(prev => prev.filter(item => item.apiId !== listing.apiId));
    } catch (err) {
      setError(err.message || "Unable to delete listing");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section style={{ maxWidth: 1240, margin: "0 auto", padding: "60px 24px" }} className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 18, alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h2 className="section-title" style={{ marginBottom: 8 }}>My Listings</h2>
          <p style={{ color: C.warmGray }}>
            {loading ? "Loading your properties..." : `${listings.length} owned propert${listings.length === 1 ? "y" : "ies"}`}
          </p>
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: 24, padding: 16, borderRadius: 8, background: "#fff5f2", color: "#9b2d18" }}>
          {error}
        </div>
      )}

      {!loading && listings.length === 0 && !error && (
        <div style={{ textAlign: "center", padding: "80px 20px", color: C.warmGray }}>
          <p style={{ fontSize: 18 }}>You have not listed any properties yet.</p>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24 }}>
        {listings.map((listing, i) => (
          <div key={listing.id} className="fade-up" style={{ animationDelay: `${i * 0.05}s` }}>
            <ListingCard listing={listing} onView={onView} />
            <button
              className="btn-outline"
              style={{ marginTop: 12, width: "100%", color: "#9b2d18", borderColor: "rgba(155, 45, 24, 0.28)" }}
              disabled={deletingId === listing.apiId}
              onClick={() => deleteListing(listing)}
            >
              {deletingId === listing.apiId ? "Deleting..." : "Delete Listing"}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
