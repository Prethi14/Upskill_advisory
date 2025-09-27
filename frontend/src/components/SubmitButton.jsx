import React from 'react';

const SubmitButton = ({ isFormValid }) => {
  return (
    <div className="text-center">
      <button
        type="submit"
        disabled={!isFormValid}
        className={`px-8 py-4 text-xl font-semibold rounded-full transition-all duration-300 transform hover:scale-105 ${
          isFormValid
            ? 'bg-[#F39F9F] text-white hover:bg-[#e68787] shadow-lg hover:shadow-xl'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        Generate My Learning Plan 🚀
      </button>
      
      {!isFormValid && (
        <p className="text-sm text-gray-500 mt-2">
          Please fill in all required fields to generate your plan
        </p>
      )}
    </div>
  );
};

export default SubmitButton;
