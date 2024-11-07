const mongoose = require('mongoose');

const FeedbackSchema = new mongoose.Schema({
  textId: {
    type: String,
    required: true,
  },
  feedback: {
    type: Number, // 1 for thumbs up, -1 for thumbs down
    enum: [1, -1],
    required: true,
  },
  timestamp: {
    type: Date,
    default: Date.now,
  },
  userId: {
    type: String,
    required: false, // Optional: Include if user authentication is implemented
  },
  context: {
    type: String,
    required: false, // Optional: Additional context if needed
  },
});

module.exports = mongoose.model('Feedback', FeedbackSchema); 