import React, { useEffect } from 'react';
import { Plus, Target } from 'lucide-react';
import SkillRow from './SkillRow.jsx';

const ManualSkillEntry = ({ formData, updateFormData, onToggle, isTransitioning }) => {
  const addSkill = () => {
    const newSkill = {
      id: Date.now().toString(),
      name: '',
      proficiency: ''
    };
    updateFormData({
      skills: [...(formData.skills || []), newSkill]
    });
  };

  const removeSkill = (id) => {
    updateFormData({
      skills: (formData.skills || []).filter(skill => skill.id !== id)
    });
  };

  const updateSkill = (id, field, value) => {
    updateFormData({
      skills: (formData.skills || []).map(skill =>
        skill.id === id ? { ...skill, [field]: value } : skill
      )
    });
  };

  // Initialize with one skill if none exist
  useEffect(() => {
    if (!formData.skills || formData.skills.length === 0) {
      addSkill();
    }
  }, []);

  return (
    <div>
      <div className="space-y-4">        
        {(!formData.skills || formData.skills.length === 0) ? (
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-2xl mb-4">
              <Target className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-lg text-gray-500 mb-2">No skills added yet</p>
            <p className="text-gray-400">Loading your first skill entry...</p>
          </div>
        ) : (
          formData.skills.map((skill) => (
            <SkillRow
              key={skill.id}
              skill={skill}
              onUpdate={updateSkill}
              onRemove={removeSkill}
            />
          ))
        )}
        
        <button
          type="button"
          onClick={addSkill}
          className="w-full py-4 px-6 border-2 border-dashed border-pink-400 text-pink-600 rounded-xl hover:bg-pink-50 hover:border-pink-500 transition-all duration-300 flex items-center justify-center font-semibold text-lg"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Another Skill
        </button>
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
          Upload your resume instead
        </button>
      </div>
    </div>
  );
};

export default ManualSkillEntry;