import logo from "../assets/Valora.png";

const ValoraLogo = ({ size = 40 }) => (
  <img src={logo} alt="Valora" width={size} height={size} style={{ objectFit: "contain" }} />
);

export default ValoraLogo;