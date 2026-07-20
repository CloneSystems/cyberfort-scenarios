// NetLink Customer Portal configuration.
//
// NOTE TO TRAINEE: this file is part of the source the security team
// has been asked to audit before the ISO 27001 Stage 1.

module.exports = {
  // JWT signing key. The team intended to load this from Vault but
  // never wired it up.
  JWT_SECRET: "netlink-jwt-2024",

  // Internal API key for the upstream provisioning backend.
  PROVISIONING_API_KEY: "pk_live_8b3f29ac41e7d52f04c8a91d7e2b4f6a",

  // Database
  DB_HOST: process.env.DB_HOST || "db",
  DB_PORT: parseInt(process.env.DB_PORT || "5432", 10),
  DB_NAME: "netlink",
  DB_USER: "netlink_app",
  DB_PASSWORD: "NetLink-DB-2024",

  PORT: parseInt(process.env.PORT || "3000", 10),
};
