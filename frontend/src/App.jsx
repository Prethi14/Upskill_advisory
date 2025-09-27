import React, { useState } from 'react';
import LandingPage from './components/LandingPage.jsx';
import Header from './components/Header.jsx';
import UserInfoSection from './components/UserInfoSection.jsx';
import SkillsInputSection from './components/SkillsInputSection.jsx';
import SubmitButton from './components/SubmitButton.jsx';

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    goalRole: '',
    skills: [],
    resume: null
  });
  const [backendResponse, setBackendResponse] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGetStarted = () => {
    setShowLanding(false);
  };

  const updateFormData = (updates) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const isFormValid = () => {
    const hasBasicInfo = formData.email && formData.goalRole;
    const hasResumeOrSkills = formData.resume || (formData.skills.length > 0 && 
      formData.skills.every(skill => skill.name && skill.proficiency));
    return hasBasicInfo && hasResumeOrSkills;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isFormValid()) {
      setIsLoading(true);
      setShowSuccessModal(true);
      setError(null);
      
      try {
        const result = await submitAdvise(formData);
        setBackendResponse(result);
        setShowSuccessModal(false);
        setShowModal(true);
      } catch (error) {
        console.error('Error submitting form:', error);
        setShowSuccessModal(false);
        setError(error.message || 'Error generating your plan. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Send advise request to backend
  async function submitAdvise(formData) {
    const url = "http://127.0.0.1:8000/advise";
    let response;

    try {
      if (formData.resume) {
        // Multipart/form-data for resume upload
        const data = new FormData();
        data.append("email", formData.email);
        data.append("goal_role", formData.goalRole);
        data.append("resume", formData.resume);
        
        // Convert skills to proper format if they exist
        if (formData.skills.length > 0) {
          const skillsObject = Object.fromEntries(
            formData.skills.map(s => [s.name, s.proficiency])
          );
          data.append("skills", JSON.stringify(skillsObject));
        }
        
        response = await fetch(url, {
          method: "POST",
          body: data
        });
      } else {
        // Multipart/form-data for manual skills entry (consistent with backend expectations)
        const data = new FormData();
        data.append("email", formData.email);
        data.append("goal_role", formData.goalRole);
        
        // Convert skills to JSON string - make sure skills have proper format
        const skillsArray = formData.skills
          .filter(skill => skill.name && skill.proficiency) // Filter out incomplete skills
          .map(skill => ({
            name: skill.name.trim(),
            proficiency: skill.proficiency
          }));
        
        if (skillsArray.length === 0) {
          throw new Error('Please add at least one skill with both name and proficiency level');
        }
        
        data.append("skills", JSON.stringify(skillsArray));
        
        response = await fetch(url, {
          method: "POST",
          body: data
        });
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return result;
      
    } catch (error) {
      console.error('Network error:', error);
      throw error;
    }
  }

  // Modal component for displaying the generated plan
  const PlanModal = ({ response, onClose }) => {
    if (!response) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto relative">
          <button
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors duration-200"
            onClick={onClose}
          >
            ×
          </button>
          
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Your Personalized Learning Plan</h2>
            <p className="text-gray-600">Here's your customized roadmap to achieve your career goals</p>
          </div>

          {/* Gap Analysis Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">!</span>
              Skills Gap Analysis
            </h3>
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="grid gap-2">
                {Object.entries(response.gap_map || {}).map(([skill, status]) => (
                  <div key={skill} className="flex justify-between items-center py-2 border-b border-red-100 last:border-b-0">
                    <span className="font-medium text-gray-800">{skill}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      status.includes('Missing') 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Courses Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">📚</span>
              Recommended Courses
            </h3>
            <div className="grid gap-4">
              {(response.recommended_courses || []).map((course, idx) => (
                <div key={idx} className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-lg font-semibold text-gray-800">{course.title}</h4>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {course.duration_weeks} weeks
                    </span>
                  </div>
                  {course.description && (
                    <p className="text-gray-600 mb-3">{course.description}</p>
                  )}
                  {course.difficulty && (
                    <p className="text-sm text-gray-500 mb-2">
                      <strong>Difficulty:</strong> {course.difficulty.charAt(0).toUpperCase() + course.difficulty.slice(1)}
                    </p>
                  )}
                  {course.url && (
                    <a 
                      href={course.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View Course →
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Timeline Section */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <h3 className="text-xl font-semibold text-gray-800 mb-2">Total Learning Timeline</h3>
            <div className="text-3xl font-bold text-green-600 mb-2">{response.timeline_weeks} weeks</div>
            <p className="text-gray-600">Complete all courses to achieve your goal role</p>
          </div>

          {/* Notes Section */}
          {response.notes && (
            <div className="mt-6 p-4 bg-gray-50 rounded-xl">
              <p className="text-sm text-gray-600">{response.notes}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Loading modal component
  const SuccessModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center">
        <div className="mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Generating Your Plan...</h2>
          <p className="text-gray-600">Please wait while we analyze your skills and prepare your personalized upskill plan.</p>
        </div>
        <div className="text-sm text-gray-500">
          This may take a few moments as we process your information with AI.
        </div>
      </div>
    </div>
  );

  // Error modal component
  const ErrorModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center">
        <div className="mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <span className="text-red-600 text-2xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
        <button
          onClick={() => setError(null)}
          className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );

  if (showLanding) {
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-25 to-indigo-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Header />
        
        <form onSubmit={handleSubmit} className="space-y-8">
          <UserInfoSection 
            formData={formData}
            updateFormData={updateFormData}
          />
          <SkillsInputSection 
            formData={formData}
            updateFormData={updateFormData}
          />
          
          <SubmitButton 
            isFormValid={isFormValid()}
            isLoading={isLoading}
          />
        </form>
        
        {/* Modals */}
        {showSuccessModal && <SuccessModal />}
        {error && <ErrorModal />}
        {showModal && backendResponse && (
          <PlanModal 
            response={backendResponse} 
            onClose={() => setShowModal(false)} 
          />
        )}
      </div>
    </div>
  );
}

export default App;