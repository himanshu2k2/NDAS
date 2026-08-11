// Run this in MongoDB Compass → Atlas connection → mongosh (_> shell)
// Usage:
//   1. Connect Compass to your Atlas cluster
//   2. Open the shell at the bottom
//   3. Paste this whole file and press Enter
//
// Creates database "ndaoms", collections, indexes, and admin user.
// Default login: admin / ChangeMe123!

const dbName = "ndaoms";
const database = db.getSiblingDB(dbName);

const collections = [
  "users",
  "clients",
  "templates",
  "documents",
  "assignments",
  "activity_logs",
];

for (const name of collections) {
  const exists = database.getCollectionNames().includes(name);
  if (!exists) {
    database.createCollection(name);
    print(`Created collection: ${name}`);
  } else {
    print(`Collection exists: ${name}`);
  }
}

database.users.createIndex({ username: 1 }, { unique: true });
database.users.createIndex({ email: 1 }, { unique: true });
database.users.createIndex({ role: 1, status: 1 });

database.clients.createIndex({ clientCode: 1 }, { unique: true });
database.clients.createIndex({ aadhaarNumber: 1 }, { unique: true });
database.clients.createIndex({ mobile: 1 });
database.clients.createIndex({ fullName: "text" });

database.templates.createIndex({ templateName: 1 }, { unique: true });
database.templates.createIndex({ isActive: 1, documentType: 1 });

database.documents.createIndex({ documentCode: 1 }, { unique: true });
database.documents.createIndex({ clientId: 1, generatedAt: -1 });
database.documents.createIndex({ documentType: 1, generatedAt: -1 });
database.documents.createIndex({ generatedBy: 1 });

database.assignments.createIndex({ assignmentCode: 1 }, { unique: true });
database.assignments.createIndex({ assignedTo: 1, status: 1 });
database.assignments.createIndex({ clientId: 1 });

database.activity_logs.createIndex({ timestamp: -1 });
database.activity_logs.createIndex({ userId: 1, timestamp: -1 });
print("Indexes ensured");

const existingAdmin = database.users.findOne({ username: "admin" });
if (existingAdmin) {
  print("Admin already exists: admin");
} else {
  const now = new Date();
  database.users.insertOne({
    fullName: "Senior Advocate",
    username: "admin",
    email: "admin@office.local",
    // bcrypt hash for ChangeMe123!
    passwordHash: "$2b$10$ypyF79hxYaGAJT.ofdFnTegrO0ouX.kpd.VdyZVhFMn2LnhN9rTcy",
    mobile: "9999999999",
    role: "admin",
    status: true,
    createdAt: now,
    updatedAt: now,
  });
  print("Admin created: admin");
}

print("Done. Refresh Compass — open database ndaoms.");
