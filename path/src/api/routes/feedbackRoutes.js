const express = require('express');
const router = express.Router();
const { submitFeedback } = require('../controllers/feedbackController');
const authMiddleware = require('../middleware/authMiddleware');

// POST /api/feedback
router.post('/', authMiddleware, submitFeedback);

module.exports = router; 