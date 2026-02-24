import { useState } from "react";
import ListingsGrid from "../components/ListingsGrid";
import C from "../constants/colors";

const ALL_TYPES  = [
  { value: "", label: "All Types" },
  { value: "house",     label: "🏠 Houses" },
  { value: "apartment", label: "🏢 Apartments" },
  { value: "office",    label: "🏙 Offices" },
  { value: "land",      label: "🌿 Land" },
];
const RENT_TYPES = ALL_TYPES.filter(t => t.value !== "land");

export default function BrowsePage({ listings, listingMode, initialType, query, onView }) {
  const [typeFilter,  setTypeFilter]  = useState(initialType || "");
  const [sortBy,      setSortBy]      = useState("default");
  const [searchInput, setSearchInput] = useState(query || "");

  const typeOptions = listingMode === "rent" ? RENT_TYPES : ALL_TYPES;

  let filtered = listings.filter(l => {
    if (listingMode && l.listing !== listingMode) return false;
    if (typeFilter  && l.type    !== typeFilter)  return false;
    if (searchInput) {
      const q = searchInput.toLowerCase();
      if (!l.name.toLowerCase().includes(q) && !l.location.toLowerCase().includes(q) && !l.type.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  if (sortBy === "price-asc")  filtered = [...filtered].sort((a, b) => a.price - b.price);
  if (sortBy === "price-desc") filtered = [...filtered].sort((a, b) => b.price - a.price);

  const title = listingMode === "buy" ? "Properties for Sale"
    : listingMode === "rent" ? "Properties for Rent"
    : "Search Results";

  return (
    <div className="fade-in">
      <div style={{ background: C.white, borderBottom: `1px solid ${C.sand}`, padding: "16px 24px" }}>
        <div style={{ maxWidth: 1240, margin: "0 auto", display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <input className="input-field" style={{ maxWidth: 280 }} placeholder="Search city, state, type..."
            value={searchInput} onChange={e => setSearchInput(e.target.value)} />
          <select className="input-field" style={{ maxWidth: 180 }} value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
            {typeOptions.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
          <select className="input-field" style={{ maxWidth: 200 }} value={sortBy} onChange={e => setSortBy(e.target.value)}>
            <option value="default">Sort: Default</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
          </select>
          {(typeFilter || sortBy !== "default" || searchInput) && (
            <button className="btn-outline" style={{ padding: "10px 18px", fontSize: 13 }}
              onClick={() => { setTypeFilter(""); setSortBy("default"); setSearchInput(""); }}>
              Clear Filters
            </button>
          )}
        </div>
      </div>
      <ListingsGrid listings={filtered} title={title} onView={onView} />
    </div>
  );
}