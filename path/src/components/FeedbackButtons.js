import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { sendFeedback } from '../api/feedback_api';
import './FeedbackButtons.css';

const FeedbackButtons = ({ textId }) => {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);

  const handleFeedback = async (rating) => {
    await sendFeedback(textId, rating);
    setFeedbackGiven(true);
    setFeedbackType(rating);
    setTimeout(() => {
      setFeedbackGiven(false);
      setFeedbackType(null);
    }, 2000); // Reset after 2 seconds
  };

  return (
    <div className="feedback-buttons">
      <button onClick={() => handleFeedback(1)} aria-label="Thumbs Up" disabled={feedbackGiven}>
        👍
      </button>
      <button onClick={() => handleFeedback(-1)} aria-label="Thumbs Down" disabled={feedbackGiven}>
        👎
      </button>
      {feedbackGiven && (
        <div className={`feedback-message ${feedbackType === 1 ? 'positive' : 'negative'}`}>
          {feedbackType === 1 ? 'Thank you for your feedback!' : 'We\'re sorry. We\'ll improve!'}
        </div>
      )}
    </div>
  );
};

FeedbackButtons.propTypes = {
  textId: PropTypes.string.isRequired,
};

export default FeedbackButtons; 