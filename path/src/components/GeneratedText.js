import React from 'react';
import PropTypes from 'prop-types';
import FeedbackButtons from './FeedbackButtons';

const GeneratedText = ({ text, textId }) => {
  return (
    <div className="generated-text">
      <p>{text}</p>
      <FeedbackButtons textId={textId} />
    </div>
  );
};

GeneratedText.propTypes = {
  text: PropTypes.string.isRequired,
  textId: PropTypes.string.isRequired,
};

export default GeneratedText; 