import React, { useState } from 'react';
import { BookOpen, Upload, Target } from 'lucide-react';
import ResumeUpload from './ResumeUpload.jsx';
import ManualSkillEntry from './ManualSkillEntry.jsx';

const SkillsInputSection = ({ formData, updateFormData }) => {
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const toggleInputMethod = () => {
    setIsTransitioning(true);
    setTimeout(() => {
      setShowManualEntry(!showManualEntry);
      setIsTransitioning(false);
    }, 300);
  };

  return (
    <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-xl border border-white/50 p-10">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-400 to-indigo-500 rounded-3xl mb-6">
          <BookOpen className="h-10 w-10 text-white" />
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-3">SKILLS</h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Choose how you'd like to share your expertise with us
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex justify-center mb-10">
        <div className="bg-gray-100 rounded-2xl p-2 inline-flex shadow-inner">
          <button
            type="button"
            onClick={() => setShowManualEntry(false)}
            className={`px-8 py-4 rounded-xl font-semibold transition-all duration-300 flex items-center gap-3 ${
              !showManualEntry
                ? 'bg-white text-pink-600 shadow-lg transform scale-105'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Upload className="h-5 w-5" />
            Upload Resume
          </button>
          <button
            type="button"
            onClick={() => setShowManualEntry(true)}
            className={`px-8 py-4 rounded-xl font-semibold transition-all duration-300 flex items-center gap-3 ${
              showManualEntry
                ? 'bg-white text-pink-600 shadow-lg transform scale-105'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Target className="h-5 w-5" />
            Manual Entry
          </button>
        </div>
      </div>

      {/* Content based on active tab */}
      <div className="max-w-2xl mx-auto">
        {!showManualEntry ? (
          <ResumeUpload 
            formData={formData}
            updateFormData={updateFormData}
            onToggle={toggleInputMethod}
            isTransitioning={isTransitioning}
          />
        ) : (
          <ManualSkillEntry 
            formData={formData}
            updateFormData={updateFormData}
            onToggle={toggleInputMethod}
            isTransitioning={isTransitioning}
          />
        )}
      </div>
    </div>
  );
};

export default SkillsInputSection;