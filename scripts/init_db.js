/**
 * Initialize NDAOMS on MongoDB Atlas (Node TLS works with Atlas;
 * Python 3.14 currently fails SSL handshake on some Windows setups).
 *
 * Usage: node scripts/init_db.js
 */
require("dotenv").config({ path: require("path").join(__dirname, "..", ".env") });

const { MongoClient } = require("mongodb");
const bcrypt = require("bcryptjs");
const fs = require("fs");
const path = require("path");

function loadEnvFile() {
  const envPath = path.join(__dirname, "..", ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const idx = trimmed.indexOf("=");
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    if (!process.env[key]) process.env[key] = value;
  }
}

loadEnvFile();

const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017";
const MONGODB_DB = process.env.MONGODB_DB || "ndaoms";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || "admin";
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || "admin@office.local";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "ChangeMe123!";
const ADMIN_FULL_NAME = process.env.ADMIN_FULL_NAME || "Senior Advocate";
const ADMIN_MOBILE = process.env.ADMIN_MOBILE || "9999999999";

const COLLECTIONS = [
  "users",
  "clients",
  "templates",
  "affidavits",
  "documents",
  "assignments",
  "activity_logs",
];

function redactedUri(uri) {
  if (!uri.includes("://") || !uri.includes("@")) return uri;
  const [scheme, rest] = uri.split("://");
  const host = rest.split("@").pop();
  return `${scheme}://***:***@${host}`;
}

async function ensureCollections(db) {
  const existing = new Set((await db.listCollections().toArray()).map((c) => c.name));
  for (const name of COLLECTIONS) {
    if (!existing.has(name)) {
      await db.createCollection(name);
      console.log(`Created collection: ${name}`);
    } else {
      console.log(`Collection exists: ${name}`);
    }
  }
}

async function ensureIndexes(db) {
  await db.collection("users").createIndex({ username: 1 }, { unique: true });
  await db.collection("users").createIndex({ email: 1 }, { unique: true });
  await db.collection("users").createIndex({ role: 1, status: 1 });

  await db.collection("clients").createIndex({ mobile: 1 });
  await db.collection("clients").createIndex({ aadhar_no: 1 }, { sparse: true });
  await db.collection("clients").createIndex({ name: "text" });

  await db.collection("templates").createIndex({ template_name: 1 }, { unique: true });
  await db.collection("templates").createIndex({ is_active: 1 });

  await db.collection("affidavits").createIndex({ client_id: 1, created_at: -1 });
  await db.collection("affidavits").createIndex({ template_id: 1, created_at: -1 });
  await db.collection("affidavits").createIndex({ status: 1 });

  await db.collection("documents").createIndex({ documentCode: 1 }, { unique: true });
  await db.collection("documents").createIndex({ clientId: 1, generatedAt: -1 });
  await db.collection("documents").createIndex({ documentType: 1, generatedAt: -1 });
  await db.collection("documents").createIndex({ generatedBy: 1 });

  await db.collection("assignments").createIndex({ assignmentCode: 1 }, { unique: true });
  await db.collection("assignments").createIndex({ assignedTo: 1, status: 1 });
  await db.collection("assignments").createIndex({ clientId: 1 });

  await db.collection("activity_logs").createIndex({ timestamp: -1 });
  await db.collection("activity_logs").createIndex({ userId: 1, timestamp: -1 });

  console.log("Indexes ensured");
}

async function seedAdmin(db) {
  const users = db.collection("users");
  const existing = await users.findOne({ username: ADMIN_USERNAME });
  if (existing) {
    console.log(`Admin already exists: ${ADMIN_USERNAME}`);
    return;
  }

  const now = new Date();
  await users.insertOne({
    fullName: ADMIN_FULL_NAME,
    username: ADMIN_USERNAME,
    email: ADMIN_EMAIL,
    passwordHash: await bcrypt.hash(ADMIN_PASSWORD, 10),
    mobile: ADMIN_MOBILE,
    role: "admin",
    status: true,
    createdAt: now,
    updatedAt: now,
  });
  console.log(`Admin created: ${ADMIN_USERNAME}`);
}

async function main() {
  const client = new MongoClient(MONGODB_URI);
  try {
    await client.connect();
    await client.db("admin").command({ ping: 1 });
    console.log(`Connected -> ${redactedUri(MONGODB_URI)} / db=${MONGODB_DB}`);

    const db = client.db(MONGODB_DB);
    await ensureCollections(db);
    await ensureIndexes(db);
    await seedAdmin(db);

    console.log("Done. Refresh MongoDB Compass (Atlas) to see the 'ndaoms' database.");
  } catch (err) {
    console.error("ERROR: Cannot initialize MongoDB.");
    console.error(`URI: ${redactedUri(MONGODB_URI)}`);
    console.error(err.message || err);
    process.exitCode = 1;
  } finally {
    await client.close();
  }
}

main();
