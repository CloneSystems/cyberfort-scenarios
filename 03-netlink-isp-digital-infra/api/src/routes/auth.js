const express = require("express");
const router = express.Router();
const { withClient } = require("../db");
const { sign } = require("../auth");

router.get("/login", (req, res) => {
  res.render("login", { error: null });
});

router.post("/login", async (req, res) => {
  const { username, password } = req.body || {};
  try {
    const row = await withClient(async (c) => {
      const r = await c.query(
        "SELECT id, username, role FROM users WHERE username = $1 AND password = $2",
        [username, password]
      );
      return r.rows[0];
    });
    if (!row) {
      return res.render("login", { error: "Invalid credentials" });
    }
    const token = sign({ id: row.id, username: row.username, role: row.role });
    res.cookie("token", token, { httpOnly: false }); // VULN-bonus: HttpOnly off
    res.redirect("/dashboard");
  } catch (e) {
    res.status(500).send("auth failure: " + e.message);
  }
});

router.get("/logout", (req, res) => {
  res.clearCookie("token");
  res.redirect("/login");
});

module.exports = router;
