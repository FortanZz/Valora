import { useState, useEffect } from "react";
import C from "../constants/colors";

const Label = ({ children, required }) => (
  <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
    {children}{required && <span style={{ color: "#c00" }}> *</span>}
  </label>
);

export default function ListPropertyModal({ user, authToken, onClose, onSubmit }) {
  const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api";
  const [form, setForm] = useState({
    name: "", type: "house", listing: "buy", price: "", location: "",
    sqft: "", beds: "", baths: "", sellerName: user?.name || "",
    phone: "", images: "", description: "",
  });
  const [err,     setErr]     = useState("");
  const [success, setSuccess] = useState(false);
  const isLand = form.type === "land";

  useEffect(() => {
    if (form.type === "land" && form.listing === "rent") {
      setForm(p => ({ ...p, listing: "buy" }));
    }
  }, [form.type, form.listing]);

  function set(k, v) { setForm(p => ({ ...p, [k]: v })); }

  function submit(e) {
    e.preventDefault();
    setErr("");
    if (!form.name.trim())       { setErr("Property name is required."); return; }
    if (!form.price || isNaN(+form.price) || +form.price <= 0) { setErr("Enter a valid price."); return; }
    if (!form.location.trim())   { setErr("Location is required."); return; }
    if (!form.sellerName.trim()) { setErr("Seller name is required."); return; }
    if (!form.phone.trim())      { setErr("Phone number is required."); return; }
    if (!authToken)              { setErr("Authentication is required to list a property."); return; }

    fetch(`${API_BASE}/properties/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        title: form.name,
        description: form.description,
        location: form.location,
        price: +form.price,
        property_type: form.type,
        category: form.listing === "rent" ? "rent" : "sale",
        contact_phone: form.phone,
        contact_email: user?.email || "",
        num_bedrooms: form.type === "land" ? null : (+form.beds || 0),
        num_bathrooms: form.type === "land" ? null : (+form.baths || 0),
        area_sqm: form.sqft ? +form.sqft : null,
        image_urls: form.images.trim() ? [form.images.trim()] : [],
      }),
    })
      .then(async response => {
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Unable to list property");
        }

        onSubmit({
          id: data.id,
          name: data.title,
          type: data.property_type,
          listing: data.category === "rent" ? "rent" : "buy",
          price: data.price,
          location: data.location,
          sqft: data.area_sqm || 0,
          beds: data.num_bedrooms || 0,
          baths: data.num_bathrooms || 0,
          seller: user?.name || data.contact_email,
          phone: data.contact_phone,
          description: data.description || "",
          img: data.image_url || "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&q=80",
        });
        setSuccess(true);
      })
      .catch(error => {
        setErr(error.message || "Unable to list property");
      });
  }

  if (success) return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()} style={{ textAlign: "center" }}>
        <h2 className="section-title" style={{ fontSize: 26, marginBottom: 12 }}>Listing Published</h2>
        <p style={{ color: C.warmGray, marginBottom: 28 }}>Your property is now live on Valora.</p>
        <button className="btn-primary" onClick={onClose}>Back to Browse</button>
      </div>
    </div>
  );

  const showBedBath = form.type === "house" || form.type === "apartment";
  const R = { marginBottom: 18 };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()} style={{ maxWidth: 620 }}>
        <button onClick={onClose} style={{
          position: "absolute", top: 16, right: 20,
          background: "none", border: "none", fontSize: 24, cursor: "pointer", color: C.warmGray,
        }}>x</button>

        <h2 className="section-title" style={{ fontSize: 26, marginBottom: 6 }}>List Your Property</h2>
        <p style={{ color: C.warmGray, fontSize: 14, marginBottom: 28 }}>Fill in the details to publish your listing on Valora.</p>

        <form onSubmit={submit}>

          <div style={R}>
            <Label required>Property Name</Label>
            <input className="input-field" placeholder="e.g. Vodno Panorama House" value={form.name} onChange={e => set("name", e.target.value)} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
            <div>
              <Label required>Property Type</Label>
              <select className="input-field" value={form.type} onChange={e => set("type", e.target.value)}>
                <option value="house">House</option>
                <option value="apartment">Apartment</option>
                <option value="office">Office</option>
                <option value="land">Land</option>
              </select>
            </div>
            <div>
              <Label required>Listing Type</Label>
              <select
                className="input-field"
                value={form.listing}
                onChange={e => set("listing", e.target.value)}
                disabled={isLand}
                style={{ opacity: isLand ? 0.6 : 1 }}
              >
                <option value="buy">For Sale</option>
                {!isLand && <option value="rent">For Rent</option>}
              </select>
              {isLand && (
                <p style={{ fontSize: 11, color: C.warmGray, marginTop: 5 }}>
                  Land can only be listed for sale.
                </p>
              )}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
            <div>
              <Label required>Price {form.listing === "rent" ? "(per month)" : ""}</Label>
              <input className="input-field" type="number" min="1" placeholder="e.g. 85000" value={form.price} onChange={e => set("price", e.target.value)} />
            </div>
            <div>
              <Label required>Location</Label>
              <input className="input-field" placeholder="City or neighborhood" value={form.location} onChange={e => set("location", e.target.value)} />
            </div>
          </div>

          {form.type !== "land" && (
            <div style={{ display: "grid", gridTemplateColumns: showBedBath ? "1fr 1fr 1fr" : "1fr", gap: 14, marginBottom: 18 }}>
              {showBedBath && (
                <>
                  <div>
                    <Label>Bedrooms</Label>
                    <input className="input-field" type="number" min="0" placeholder="3" value={form.beds} onChange={e => set("beds", e.target.value)} />
                  </div>
                  <div>
                    <Label>Bathrooms</Label>
                    <input className="input-field" type="number" min="0" placeholder="2" value={form.baths} onChange={e => set("baths", e.target.value)} />
                  </div>
                </>
              )}
              <div>
                <Label>Square Meters</Label>
                <input className="input-field" type="number" min="1" placeholder="85" value={form.sqft} onChange={e => set("sqft", e.target.value)} />
              </div>
            </div>
          )}

          <div style={R}>
            <Label>Description</Label>
            <textarea className="input-field" rows={3} placeholder="Describe your property..." value={form.description} onChange={e => set("description", e.target.value)} style={{ resize: "vertical" }} />
          </div>

          <div style={R}>
            <Label>Photo URL (optional)</Label>
            <input className="input-field" placeholder="https://..." value={form.images} onChange={e => set("images", e.target.value)} />
          </div>

          <div style={{ borderTop: `1px solid ${C.sand}`, paddingTop: 20, marginBottom: 18 }}>
            <p style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: C.warmGray, marginBottom: 16 }}>
              Seller Information
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
              <div>
                <Label required>Seller Name</Label>
                <input className="input-field" placeholder="Full name" value={form.sellerName} onChange={e => set("sellerName", e.target.value)} />
              </div>
              <div>
                <Label required>Phone Number</Label>
                <input className="input-field" placeholder="+389 70 000 000" value={form.phone} onChange={e => set("phone", e.target.value)} />
              </div>
            </div>
          </div>

          {err && (
            <p style={{ color: "#c00", fontSize: 13, marginBottom: 14 }}>{err}</p>
          )}

          <button type="submit" className="btn-primary" style={{ width: "100%", padding: 14, fontSize: 16 }}>
            Publish Listing
          </button>

        </form>
      </div>
    </div>
  );
}
