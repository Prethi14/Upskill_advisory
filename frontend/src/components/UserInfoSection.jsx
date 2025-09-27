import React from 'react';
import { User, Mail, Target, ChevronDown, TrendingUp } from 'lucide-react';
import { GOAL_ROLES } from '../constants/roles.js';

const UserInfoSection = ({ formData, updateFormData }) => {
  return (
    <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-xl border border-white/50 p-10">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-pink-400 to-purple-500 rounded-2xl mb-4">
          <Target className="h-8 w-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Tell Us About Yourself</h2>
        <p className="text-gray-600">Help us understand your background and aspirations</p>
      </div>
      
      <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
        {/* Email Input */}
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-3">
            Email Address *
          </label>
          <div className="relative group">
            <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-pink-500 transition-colors duration-200" />
            <input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => updateFormData({ email: e.target.value })}
              placeholder="your.email@example.com"
              className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-100 focus:border-pink-400 transition-all duration-200 text-lg"
            />
          </div>
        </div>

        {/* Goal Role Dropdown */}
        <div className="space-y-2">
          <label htmlFor="goalRole" className="block text-sm font-semibold text-gray-700 mb-3">
            Goal Role *
          </label>
          <div className="relative group">
            <TrendingUp className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-pink-500 transition-colors duration-200 z-10" />
            <select
              id="goalRole"
              required
              value={formData.goalRole}
              onChange={(e) => updateFormData({ goalRole: e.target.value })}
              className="w-full pl-12 pr-12 py-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-100 focus:border-pink-400 transition-all duration-200 appearance-none bg-white hover:border-pink-300 hover:shadow-md cursor-pointer text-lg font-medium text-gray-700"
            >
              <option value="" className="text-gray-400">e.g., SDET, GenAI QA, Full Stack Developer</option>
              {GOAL_ROLES.map(role => (
                <option key={role} value={role} className="text-gray-700 py-3">{role}</option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <ChevronDown className="w-5 h-5 text-pink-400 group-focus-within:text-pink-500 transition-colors duration-200" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserInfoSection;