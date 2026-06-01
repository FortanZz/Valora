import { useEffect, useState } from "react";
import Navbar            from "./components/Navbar";
import Footer            from "./components/Footer";
import AuthModal         from "./components/AuthModal";
import ListPropertyModal from "./components/ListPropertyModal";
import ListingModal      from "./components/ListingModal";
import HomePage          from "./pages/HomePage";
import BrowsePage        from "./pages/BrowsePage";
import AboutPage         from "./pages/AboutPage";
import ContactPage       from "./pages/ContactPage";
import MyListingsPage    from "./pages/MyListingsPage";
import LISTINGS          from "./data/listings";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api";

function mapApiProperty(property) {
  return {
    id: `api-${property.id}`,
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

export default function App() {
  const [page,        setPage]        = useState("home");
  const [listingMode, setListingMode] = useState(null);
  const [typeFilter,  setTypeFilter]  = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy,      setSortBy]      = useState("default");
  const [listings,    setListings]    = useState(LISTINGS);
  const [viewListing, setViewListing] = useState(null);
  const [authModal,   setAuthModal]   = useState(null);
  const [showList,    setShowList]    = useState(false);
  const [user,        setUser]        = useState(null);
  const [authToken,   setAuthToken]   = useState("");

  useEffect(() => {
    async function loadListings() {
      if (!["browse", "buy", "rent"].includes(page)) {
        return;
      }

      const query = new URLSearchParams();
      if (searchQuery) query.append("query", searchQuery);
      if (typeFilter) query.append("property_type", typeFilter);
      if (listingMode === "buy") query.append("category", "sale");
      if (listingMode === "rent") query.append("category", "rent");
      if (sortBy && sortBy !== "default") query.append("sort_by", sortBy);
      query.append("limit", "50");

      try {
        const response = await fetch(`${API_BASE}/properties/search?${query.toString()}`);
        if (!response.ok) {
          throw new Error(`Failed to load properties: ${response.status}`);
        }
        const results = await response.json();
        const apiListings = results.map(mapApiProperty);
        setListings(apiListings.length ? [...apiListings, ...LISTINGS] : LISTINGS);
      } catch (error) {
        console.error(error);
        setListings(LISTINGS);
      }
    }

    loadListings();
  }, [page, listingMode, typeFilter, searchQuery, sortBy]);

  function navigate(p, subtype = null) {
    if (p === "sell") {
      if (!user) { setAuthModal("register"); }
      else        { setShowList(true); }
      return;
    }
    setPage(p);
    setTypeFilter(subtype || null);
    setListingMode(p === "buy" ? "buy" : p === "rent" ? "rent" : null);
    setSortBy("default");
    setSearchQuery("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleSearch(query, listingType) {
    setPage("browse");
    setListingMode(listingType || null);
    setTypeFilter(null);
    setSortBy("default");
    setSearchQuery(query);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleFilterChange(newType) {
    setTypeFilter(newType);
    setSearchQuery("");
  }

  function handleSortChange(newSort) {
    setSortBy(newSort);
  }

  function renderPage() {
    switch (page) {
      case "home":
        return <HomePage listings={listings} onSearch={handleSearch} onView={setViewListing} />;
      case "buy":
      case "rent":
      case "browse":
        return (
          <BrowsePage
            listings={listings}
            listingMode={listingMode}
            typeFilter={typeFilter || ""}
            query={searchQuery}
            sortBy={sortBy}
            onTypeFilter={handleFilterChange}
            onSearch={setSearchQuery}
            onSort={handleSortChange}
            onView={setViewListing}
          />
        );
      case "about":
        return <AboutPage />;
      case "contact":
        return <ContactPage />;
      case "my-listings":
        return <MyListingsPage authToken={authToken} onView={setViewListing} />;
      default:
        return <HomePage listings={listings} onSearch={handleSearch} onView={setViewListing} />;
    }
  }

  return (
    <>
      <Navbar
        onNav={navigate} activePage={page} user={user}
        onAuth={m => setAuthModal(m)} onLogout={() => { setUser(null); setAuthToken(""); }}
        onListProperty={() => setShowList(true)}
        onMyListings={() => navigate("my-listings")}
      />

      <main style={{ minHeight: "calc(100vh - 68px - 260px)" }}>
        {renderPage()}
      </main>

      <Footer onNav={navigate} />

      {viewListing && <ListingModal listing={viewListing} onClose={() => setViewListing(null)} />}

      {authModal && (
        <AuthModal mode={authModal} onClose={() => setAuthModal(null)}
          onSuccess={auth => { setUser({ name: auth.user.first_name + " " + auth.user.last_name, email: auth.user.email }); setAuthToken(auth.access_token); setAuthModal(null); }} />
      )}

      {showList && (
        <ListPropertyModal user={user} authToken={authToken} onClose={() => setShowList(false)}
          onSubmit={newListing => setListings(prev => [newListing, ...prev])} />
      )}
    </>
  );
}
