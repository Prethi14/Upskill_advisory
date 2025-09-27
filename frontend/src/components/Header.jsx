import React from 'react';
import { Target } from 'lucide-react';

const Header = () => {
  return (
    <div className="text-center mb-8">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-[#F39F9F] rounded-full mb-4">
        <Target className="w-8 h-8 text-white" />
      </div>
      <h1 className="text-4xl font-bold text-gray-800 mb-2">SkillUp Ai</h1>
      <p className="text-xl text-gray-600">Find Your Perfect Learning Path</p>
    </div>
  );
};

export default Header;