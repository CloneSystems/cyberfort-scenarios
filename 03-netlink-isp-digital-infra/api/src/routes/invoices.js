const express = require("express");
const router = express.Router();
const { withClient } = require("../db");
const { authRequired } = require("../auth");

router.get("/api/invoices/:id", authRequired, async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isFinite(id)) return res.status(400).json({ error: "bad id" });
  try {
    // VULN-3 (CWE-639 / IDOR): the query fetches an invoice by primary
    // key with no check that the logged-in user owns it. Any
    // authenticated customer can read any other customer's invoice
    // by guessing IDs.
    const inv = await withClient(async (c) => {
      const r = await c.query(
        "SELECT i.id, i.customer_id, c.name AS customer_name, c.email, " +
        "       i.amount_eur, i.period, i.status, i.notes " +
        "FROM invoices i JOIN customers c ON c.id = i.customer_id " +
        "WHERE i.id = $1",
        [id]
      );
      return r.rows[0];
    });
    if (!inv) return res.status(404).json({ error: "not found" });
    res.json(inv);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

router.get("/api/me/invoices", authRequired, async (req, res) => {
  try {
    const rows = await withClient(async (c) => {
      const r = await c.query(
        "SELECT i.id, i.amount_eur, i.period, i.status FROM invoices i " +
        "JOIN customers c ON c.id = i.customer_id " +
        "WHERE c.user_id = $1 ORDER BY i.id DESC",
        [req.user.id]
      );
      return r.rows;
    });
    res.json({ invoices: rows });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

module.exports = router;
