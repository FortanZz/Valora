import { useState } from "react";
import Navbar            from "./components/Navbar";
import Footer            from "./components/Footer";
import AuthModal         from "./components/AuthModal";
import ListPropertyModal from "./components/ListPropertyModal";
import ListingModal      from "./components/ListingModal";
import HomePage          from "./pages/HomePage";
import BrowsePage        from "./pages/BrowsePage";
import AboutPage         from "./pages/AboutPage";
import ContactPage       from "./pages/ContactPage";
import LISTINGS          from "./data/listings";

export default function App() {
  const [page,        setPage]        = useState("home");
  const [listingMode, setListingMode] = useState(null);
  const [typeFilter,  setTypeFilter]  = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [listings,    setListings]    = useState(LISTINGS);
  const [viewListing, setViewListing] = useState(null);
  const [authModal,   setAuthModal]   = useState(null);
  const [showList,    setShowList]    = useState(false);
  const [user,        setUser]        = useState(null);

  function navigate(p, subtype = null) {
    if (p === "sell") {
      if (!user) { setAuthModal("register"); }
      else        { setShowList(true); }
      return;
    }
    setPage(p);
    setTypeFilter(subtype || null);
    setListingMode(p === "buy" ? "buy" : p === "rent" ? "rent" : null);
    setSearchQuery("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleSearch(query, listingType) {
    setPage("browse");
    setListingMode(listingType || null);
    setTypeFilter(null);
    setSearchQuery(query);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function renderPage() {
    switch (page) {
      case "home":
        return <HomePage listings={listings} onSearch={handleSearch} onView={setViewListing} />;
      case "buy":
      case "rent":
      case "browse":
        return <BrowsePage listings={listings} listingMode={listingMode} initialType={typeFilter} query={searchQuery} onView={setViewListing} />;
      case "about":
        return <AboutPage />;
      case "contact":
        return <ContactPage />;
      default:
        return <HomePage listings={listings} onSearch={handleSearch} onView={setViewListing} />;
    }
  }

  return (
    <>
      <Navbar
        onNav={navigate} activePage={page} user={user}
        onAuth={m => setAuthModal(m)} onLogout={() => setUser(null)}
        onListProperty={() => setShowList(true)}
      />

      <main style={{ minHeight: "calc(100vh - 68px - 260px)" }}>
        {renderPage()}
      </main>

      <Footer onNav={navigate} />

      {viewListing && <ListingModal listing={viewListing} onClose={() => setViewListing(null)} />}

      {authModal && (
        <AuthModal mode={authModal} onClose={() => setAuthModal(null)}
          onSuccess={u => { setUser(u); setAuthModal(null); }} />
      )}

      {showList && (
        <ListPropertyModal user={user} onClose={() => setShowList(false)}
          onSubmit={newListing => setListings(prev => [newListing, ...prev])} />
      )}
    </>
  );
}