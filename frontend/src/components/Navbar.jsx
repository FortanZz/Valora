import { useState, useRef, useEffect } from "react";
import ValoraLogo from "./ValoraLogo";

const BUY_ITEMS  = [
  { label: "Houses"     },
  { label: "Apartments" },
  { label: "Offices"    },
  { label: "Land"       },
];
const RENT_ITEMS = [
  { label: "Houses"     },
  { label: "Apartments" },
  { label: "Offices"    },
];

function NavBtn({ label, active, onClick, children, ...props }) {
  return (
    <button
      className={`nav-btn${active ? " is-active" : ""}`}
      onClick={onClick}
      {...props}
    >
      {label}{children}
    </button>
  );
}

export default function Navbar({ onNav, activePage, user, onAuth, onLogout, onListProperty }) {
  const [buyOpen,     setBuyOpen]     = useState(false);
  const [rentOpen,    setRentOpen]    = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const buyRef = useRef(); const rentRef = useRef(); const profileRef = useRef();

  useEffect(() => {
    function handler(e) {
      if (buyRef.current     && !buyRef.current.contains(e.target))     setBuyOpen(false);
      if (rentRef.current    && !rentRef.current.contains(e.target))    setRentOpen(false);
      if (profileRef.current && !profileRef.current.contains(e.target)) setProfileOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <header className="nav-shell">
      <div className="nav-inner">

        <button className="nav-brand" onClick={() => onNav("home")}>
          <ValoraLogo size={38} />
          <span className="nav-wordmark">Valora</span>
        </button>

        <nav className="nav-links">
          <div ref={buyRef} style={{ position: "relative" }}>
            <NavBtn label="Buy" active={activePage === "buy"} onClick={() => onNav("buy")}
              onMouseEnter={() => { setBuyOpen(true); setRentOpen(false); }}>
              <span style={{ fontSize: 11 }}>v</span>
            </NavBtn>
            {buyOpen && (
              <div className="nav-dropdown" onMouseLeave={() => setBuyOpen(false)}>
                {BUY_ITEMS.map(it => (
                  <button key={it.label} className="nav-dropdown-item"
                    onClick={() => { onNav("buy", it.label.toLowerCase()); setBuyOpen(false); }}>
                    {it.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div ref={rentRef} style={{ position: "relative" }}>
            <NavBtn label="Rent" active={activePage === "rent"} onClick={() => onNav("rent")}
              onMouseEnter={() => { setRentOpen(true); setBuyOpen(false); }}>
              <span style={{ fontSize: 11 }}>v</span>
            </NavBtn>
            {rentOpen && (
              <div className="nav-dropdown" onMouseLeave={() => setRentOpen(false)}>
                {RENT_ITEMS.map(it => (
                  <button key={it.label} className="nav-dropdown-item"
                    onClick={() => { onNav("rent", it.label.toLowerCase()); setRentOpen(false); }}>
                    {it.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <NavBtn label="Sell"    active={activePage === "sell"}    onClick={() => { if (!user) onAuth("register"); else onListProperty(); }} />
          <NavBtn label="About"   active={activePage === "about"}   onClick={() => onNav("about")} />
          <NavBtn label="Contact" active={activePage === "contact"} onClick={() => onNav("contact")} />
        </nav>

        <div className="nav-actions">
          {user ? (
            <div ref={profileRef} style={{ position: "relative" }}>
              <button className="profile-button" onClick={() => setProfileOpen(p => !p)}>
                {user.name[0].toUpperCase()}
              </button>
              {profileOpen && (
                <div className="nav-dropdown" style={{ right: 0, left: "auto", transform: "none", minWidth: 190 }}>
                  <button className="nav-dropdown-item" style={{ fontWeight: 700, cursor: "default" }}>{user.name}</button>
                  <button className="nav-dropdown-item" onClick={() => { onListProperty(); setProfileOpen(false); }}>List a Property</button>
                  <button className="nav-dropdown-item" style={{ color: "#c00" }} onClick={() => { onLogout(); setProfileOpen(false); }}>Sign Out</button>
                </div>
              )}
            </div>
          ) : (
            <>
              <button className="btn-outline" style={{ padding: "8px 18px", fontSize: 14 }} onClick={() => onAuth("login")}>Sign In</button>
              <button className="btn-primary" style={{ padding: "8px 18px", fontSize: 14 }} onClick={() => onAuth("register")}>Join Free</button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
