const express = require('express');
const router = express.Router();
const { getTimingCollection } = require('./db');

// Start webcam timing
router.post('/start', async (req, res) => {
    try {
        const startTime = new Date();
        const result = await getTimingCollection().insertOne({ start_time: startTime });
        res.status(200).json({ message: "Webcam started", start_time: startTime });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Stop webcam timing
router.post('/stop', async (req, res) => {
    try {
        const stopTime = new Date();
        await getTimingCollection().updateOne(
            { /* query criteria */ },
            { $set: { stop_time: stopTime } }
        );
        res.status(200).json({ message: "Webcam stopped", stop_time: stopTime });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
