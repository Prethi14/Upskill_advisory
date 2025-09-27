import React from 'react';
import { X, ChevronDown } from 'lucide-react';
import { SKILL_SUGGESTIONS, PROFICIENCY_LEVELS } from '../constants/skills.js';

const SkillRow = ({ skill, onUpdate, onRemove }) => {
  // Get all unique skills from all roles
  const getAllSkills = () => {
    const allSkills = new Set();
    Object.values(SKILL_SUGGESTIONS).forEach(roleSkills => {
      roleSkills.forEach(skillName => allSkills.add(skillName));
    });
    return Array.from(allSkills).sort();
  };

  return (
    <div className="flex gap-4 items-start bg-gray-50 p-6 rounded-xl border border-gray-200 hover:border-pink-200 hover:bg-pink-25 transition-all duration-200">
      <div className="flex-1">
        <input
          type="text"
          placeholder="Skill name (e.g., JavaScript, Python)"
          value={skill.name}
          onChange={(e) => onUpdate(skill.id, 'name', e.target.value)}
          list={`skills-${skill.id}`}
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-pink-100 focus:border-pink-400 transition-all duration-200 text-base font-medium"
          required
        />
        <datalist id={`skills-${skill.id}`}>
          {getAllSkills().map(suggestion => (
            <option key={suggestion} value={suggestion} />
          ))}
        </datalist>
      </div>
      
      <div className="w-44 relative">
        <select
          value={skill.proficiency}
          onChange={(e) => onUpdate(skill.id, 'proficiency', e.target.value)}
          className="w-full px-4 py-3 pr-10 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-pink-100 focus:border-pink-400 appearance-none bg-white hover:border-pink-300 hover:shadow-md cursor-pointer text-gray-700 font-medium transition-all duration-200"
          required
        >
          <option value="" className="text-gray-400">Select Level</option>
          {PROFICIENCY_LEVELS.map(level => (
            <option key={level} value={level} className="text-gray-700">{level}</option>
          ))}
        </select>
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <ChevronDown className="w-5 h-5 text-pink-400" />
        </div>
      </div>
      
      <button
        type="button"
        onClick={() => onRemove(skill.id)}
        className="p-3 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};

export default SkillRow;