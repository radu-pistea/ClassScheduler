import React from 'react';

const GenerateButton = ({ onClick, isLoading }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`px-4 py-2 rounded-md text-white font-medium ${
        isLoading
          ? 'bg-gray-400 cursor-not-allowed'
          : 'bg-blue-600 hover:bg-blue-700'
      }`}
    >
      {isLoading ? 'Generating...' : 'Generate Schedule'}
    </button>
  );
};

export default GenerateButton; 