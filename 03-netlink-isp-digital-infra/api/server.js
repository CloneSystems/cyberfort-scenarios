const path = require("path");
const express = require("express");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");

const cfg = require("./src/config");
const { withClient } = require("./src/db");
const { authRequired } = require("./src/auth");

const authRoutes = require("./src/routes/auth");
const customerRoutes = require("./src/routes/customers");
const invoiceRoutes = require("./src/routes/invoices");
const adminRoutes = require("./src/routes/admin");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cookieParser());

app.get("/", (req, res) => res.redirect("/dashboard"));

app.get("/dashboard", authRequired, async (req, res) => {
  try {
    const data = await withClient(async (c) => {
      const cust = await c.query(
        "SELECT plan FROM customers WHERE user_id = $1",
        [req.user.id]
      );
      const inv = await c.query(
        "SELECT i.id, i.amount_eur, i.period, i.status " +
        "FROM invoices i JOIN customers c ON c.id = i.customer_id " +
        "WHERE c.user_id = $1 ORDER BY i.id DESC",
        [req.user.id]
      );
      return { plan: (cust.rows[0] && cust.rows[0].plan) || "—", invoices: inv.rows };
    });
    res.render("dashboard", {
      user: req.user,
      plan: data.plan,
      nextBill: "first of next month",
      invoices: data.invoices,
    });
  } catch (e) {
    res.status(500).send("dashboard error: " + e.message);
  }
});

app.get("/healthz", (req, res) => res.json({ status: "ok" }));

app.use(authRoutes);
app.use(customerRoutes);
app.use(invoiceRoutes);
app.use(adminRoutes);

app.listen(cfg.PORT, "0.0.0.0", () => {
  console.log(`NetLink customer portal listening on :${cfg.PORT}`);
});
