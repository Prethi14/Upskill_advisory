import React, { useState, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

const ResumeUpload = ({ formData, updateFormData, onToggle, isTransitioning }) => {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = (file) => {
    updateFormData({ resume: file });
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
          dragActive ? 'border-pink-400 bg-pink-50 scale-105' : 'border-gray-300 hover:border-pink-400 hover:bg-pink-25'
        } ${formData.resume ? 'bg-green-50 border-green-400' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileInputChange}
          className="hidden"
        />
        
        {formData.resume ? (
          <div>
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-2xl mb-6">
              <FileText className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-700 mb-3">Resume Uploaded!</p>
            <p className="text-lg text-green-600 font-medium">{formData.resume.name}</p>
            <p className="text-sm text-gray-500 mt-2">Click to upload a different file</p>
          </div>
        ) : (
          <div>
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-3xl mb-6">
              <Upload className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-700 mb-3">Upload Your Resume</p>
            <p className="text-lg text-gray-500 mb-6">Drag and drop your resume here, or click to browse</p>
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-pink-100 text-pink-700 rounded-full text-sm font-medium">
              <FileText className="w-4 h-4" />
              Supports PDF, DOC, DOCX files
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-8 text-center">
        <div className="flex items-center justify-center space-x-4">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="px-4 text-gray-500 font-medium">OR</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>
        <button
          type="button"
          onClick={onToggle}
          disabled={isTransitioning}
          className="mt-4 text-pink-600 hover:text-pink-700 font-medium underline transition-colors duration-200 disabled:opacity-50"
        >
        </button>
      </div>
    </div>
  );
};

export default ResumeUpload;