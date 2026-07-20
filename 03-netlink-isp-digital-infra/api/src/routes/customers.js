const express = require("express");
const router = express.Router();
const { withClient } = require("../db");
const { authRequired } = require("../auth");

router.get("/api/customers/search", authRequired, async (req, res) => {
  const q = req.query.q || "";
  try {
    // VULN-1 (CWE-89): the developer concatenated user input directly
    // into the SQL string because "we only call this from the admin UI".
    const sql =
      "SELECT id, name, email, plan FROM customers " +
      "WHERE name ILIKE '%" + q + "%' OR email ILIKE '%" + q + "%' " +
      "ORDER BY name LIMIT 50";
    const rows = await withClient(async (c) => (await c.query(sql)).rows);
    res.json({ query: q, results: rows });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

module.exports = router;
