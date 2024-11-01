require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const feedbackRoutes = require('./routes/feedbackRoutes');
const { processFeedback } = require('./services/feedbackService');
const { analyzeFeedback } = require('./services/feedbackAnalyzer');
const cron = require('node-cron');
const logger = require('./utils/logger');
const morgan = require('morgan');

const app = express();

// Middleware
app.use(express.json());

// Use morgan for HTTP request logging
app.use(morgan('combined', { stream: logger.stream }));

// Routes
app.use('/api/feedback', feedbackRoutes);

// Schedule the feedback processing every day at midnight
cron.schedule('0 0 * * *', () => {
  console.log('Processing and analyzing feedback...');
  processFeedback();
  analyzeFeedback();
});

// Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Connect to MongoDB and Start Server
mongoose
  .connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => {
    console.log('Connected to MongoDB');
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
  })
  .catch((err) => {
    console.error('MongoDB connection error:', err);
  }); 