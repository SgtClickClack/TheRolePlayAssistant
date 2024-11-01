const Feedback = require('../models/Feedback');
const logger = require('../utils/logger');

/**
 * @desc    Submit user feedback
 * @route   POST /api/feedback
 * @access  Public
 * @param   {string} textId - Identifier for the generated text
 * @param   {number} feedback - 1 for thumbs up, -1 for thumbs down
 * @param   {string} [context] - Optional context information
 */
exports.submitFeedback = async (req, res) => {
  const { textId, feedback, context } = req.body;
  const userId = req.user; // Retrieved from auth middleware

  if (![1, -1].includes(feedback)) {
    logger.warn('Invalid feedback value received:', feedback);
    return res.status(400).json({ message: 'Invalid feedback value.' });
  }

  try {
    const newFeedback = new Feedback({
      textId,
      feedback,
      userId,
      context,
    });

    await newFeedback.save();
    logger.info(`Feedback submitted: UserID=${userId}, TextID=${textId}, Feedback=${feedback}`);
    res.status(201).json({ message: 'Feedback submitted successfully.' });
  } catch (error) {
    logger.error('Error submitting feedback:', error);
    res.status(500).json({ message: 'Server error.' });
  }
}; 