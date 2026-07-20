const jwt = require("jsonwebtoken");
const cfg = require("./config");

function sign(payload) {
  return jwt.sign(payload, cfg.JWT_SECRET, { expiresIn: "8h" });
}

function authRequired(req, res, next) {
  const token = req.cookies && req.cookies.token;
  if (!token) return res.redirect("/login");
  try {
    req.user = jwt.verify(token, cfg.JWT_SECRET);
    return next();
  } catch (e) {
    return res.redirect("/login");
  }
}

function adminRequired(req, res, next) {
  authRequired(req, res, () => {
    // VULN-2: the JWT is signed with a hardcoded secret. Anyone who
    // reads src/config.js can mint themselves an admin token.
    if (req.user && req.user.role === "admin") return next();
    return res.status(403).send("admin only");
  });
}

module.exports = { sign, authRequired, adminRequired };
