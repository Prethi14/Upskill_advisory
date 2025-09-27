import React from 'react';
import { Clock } from 'lucide-react';

function PreferencesSection({ preferences, updateFormData }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    updateFormData({
      preferences: {
        ...preferences,
        [name]: value
      }
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      {/* Heading */}
      <div className="flex items-center space-x-3 mb-6">
        <Clock className="h-6 w-6 text-purple-500" />
        <h3 className="text-xl font-semibold text-gray-800">
          Preferences (Optional)
        </h3>
      </div>

      {/* Input field */}
      <div className="space-y-2">
        <label className="text-gray-700 font-medium">
          Max Plan Duration <span className="text-sm text-gray-400">(weeks)</span>
        </label>
        <input
          type="number"
          name="maxDuration"
          value={preferences.maxDuration}
          onChange={handleChange}
          min={1}
          placeholder="e.g. 12"
          className="w-full px-4 py-3 border border-gray-300 rounded-xl text-gray-700 
                     focus:outline-none focus:ring-2 focus:ring-purple-400"
        />
        <p className="text-sm text-gray-500">
          Set a limit for your learning plan
        </p>
      </div>
    </div>
  );
}

export default PreferencesSection;
