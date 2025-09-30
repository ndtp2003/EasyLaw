// MongoDB initialization script for EasyLaw
// This script runs when MongoDB container starts for the first time

db = db.getSiblingDB('easylaw_dev');

// Create collections
db.createCollection('users');
db.createCollection('sessions');
db.createCollection('messages');
db.createCollection('admin_logs');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });
db.users.createIndex({ "status": 1 });
db.users.createIndex({ "created_at": 1 });

db.sessions.createIndex({ "user_id": 1 });
db.sessions.createIndex({ "status": 1 });
db.sessions.createIndex({ "mode": 1 });
db.sessions.createIndex({ "created_at": -1 });

db.messages.createIndex({ "session_id": 1 });
db.messages.createIndex({ "sender": 1 });
db.messages.createIndex({ "created_at": -1 });

db.admin_logs.createIndex({ "admin_id": 1 });
db.admin_logs.createIndex({ "action": 1 });
db.admin_logs.createIndex({ "created_at": -1 });
db.admin_logs.createIndex({ "success": 1 });

// Insert default admin user (password: admin123)
// Note: In production, this should be done securely
db.users.insertOne({
    email: "admin@easylaw.dev",
    password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewstMnWpEJBr.5pe", // admin123
    role: "admin",
    status: "active",
    created_at: new Date(),
    updated_at: new Date()
});

print('EasyLaw database initialized successfully!');
