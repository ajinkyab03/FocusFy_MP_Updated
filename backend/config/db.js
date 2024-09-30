const { MongoClient } = require('mongodb');

const url = 'mongodb://localhost:27017';
const dbName = 'webcam_db';

let db;

async function connectDB() {
    const client = new MongoClient(url, { useNewUrlParser: true, useUnifiedTopology: true });
    await client.connect();
    db = client.db(dbName);
}

function getTimingCollection() {
    return db.collection('timing');
}

module.exports = { connectDB, getTimingCollection };
