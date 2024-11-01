const express = require('express');
const router = express.Router();
const { getFeedbackSummary } = require('../controllers/metricsController');

// GET /api/metrics/feedback-summary
router.get('/feedback-summary', getFeedbackSummary);

module.exports = router; 