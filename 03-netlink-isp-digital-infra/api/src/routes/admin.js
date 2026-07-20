const express = require("express");
const router = express.Router();
const cfg = require("../config");
const { adminRequired } = require("../auth");

// VULN-5: "diagnostics" endpoint that leaks the full DB password and
// the upstream provisioning API key in the response body. Restricted
// to admin-role JWTs — but the JWT signing secret is hardcoded in
// src/config.js, so a trainee who has read the source can forge one.
router.get("/api/admin/diagnostics", adminRequired, (req, res) => {
  res.json({
    portal_version: "2.4.1",
    node_version: process.version,
    db: {
      host: cfg.DB_HOST,
      port: cfg.DB_PORT,
      user: cfg.DB_USER,
      password: cfg.DB_PASSWORD,
      database: cfg.DB_NAME,
    },
    upstream: {
      provisioning_api_key: cfg.PROVISIONING_API_KEY,
    },
    jwt_secret_first_chars: cfg.JWT_SECRET.slice(0, 4) + "...",
  });
});

module.exports = router;
