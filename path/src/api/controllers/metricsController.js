const Feedback = require('../models/Feedback');
const logger = require('../utils/logger');

exports.getFeedbackSummary = async (req, res) => {
  try {
    const summary = await Feedback.aggregate([
      {
        $group: {
          _id: "$feedback",
          count: { $sum: 1 }
        }
      }
    ]);
    res.status(200).json(summary);
  } catch (error) {
    logger.error('Error fetching feedback summary:', error);
    res.status(500).json({ message: 'Server error.' });
  }
}; 