import React from 'react';
import { Brain, Sparkles, Target, BookOpen, TrendingUp, ArrowRight, CheckCircle } from 'lucide-react';

const LandingPage = ({ onGetStarted }) => {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Advanced algorithms analyze your skills and career goals to create personalized recommendations"
    },
    {
      icon: Target,
      title: "Goal-Oriented Planning",
      description: "Get a clear roadmap tailored to your specific career aspirations and target roles"
    },
    {
      icon: BookOpen,
      title: "Curated Learning Paths",
      description: "Access hand-picked courses and resources from top platforms to accelerate your growth"
    },
    {
      icon: TrendingUp,
      title: "Skills Gap Analysis",
      description: "Identify exactly what skills you need to develop to reach your next career milestone"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Software Engineer",
      content: "SkillUp AI helped me transition from frontend to full-stack development in just 6 months!",
      avatar: "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop"
    },
    {
      name: "Marcus Johnson",
      role: "Data Scientist",
      content: "The personalized learning plan was exactly what I needed to break into machine learning.",
      avatar: "https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop"
    },
    {
      name: "Elena Rodriguez",
      role: "Product Manager",
      content: "Amazing tool! It identified skills I didn't even know I was missing for my dream role.",
      avatar: "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-25 to-indigo-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 max-w-6xl">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-r from-pink-400 via-purple-500 to-indigo-600 rounded-full mb-8 shadow-2xl">
            <Brain className="h-16 w-16 text-white" />
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Skill<span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-600">Up</span> AI
          </h1>
          
          <p className="text-2xl md:text-3xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed">
            Transform your career with AI-powered skill analysis and personalized learning recommendations
          </p>
          
          <div className="flex items-center justify-center gap-3 text-purple-600 font-medium mb-12">
            <Sparkles className="h-6 w-6" />
            <span className="text-lg">Powered by AI</span>
            <Sparkles className="h-6 w-6" />
          </div>

          {/* CTA Button */}
          <button
            onClick={onGetStarted}
            className="group px-12 py-6 text-2xl font-bold bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center mx-auto gap-4"
          >
            Get Your Personalized Plan
            <ArrowRight className="h-6 w-6 group-hover:translate-x-1 transition-transform" />
          </button>
          
          <p className="text-gray-500 mt-4 text-lg">Free • No signup required • Instant results</p>
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-4">
            Why Choose SkillUp AI?
          </h2>
          <p className="text-xl text-gray-600 text-center mb-12 max-w-3xl mx-auto">
            Our intelligent platform combines cutting-edge AI with industry expertise to accelerate your career growth
          </p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/50 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-pink-400 to-purple-500 rounded-2xl mb-6">
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How It Works Section */}
        <div className="mb-20">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-pink-400 to-purple-500 rounded-full text-white text-2xl font-bold mb-6">
                1
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Share Your Info</h3>
              <p className="text-gray-600 text-lg">Tell us about your current skills and career goals. Upload your resume or enter skills manually.</p>
            </div>
            
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-400 to-indigo-500 rounded-full text-white text-2xl font-bold mb-6">
                2
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">AI Analysis</h3>
              <p className="text-gray-600 text-lg">Our AI analyzes your profile against industry requirements and identifies skill gaps.</p>
            </div>
            
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-indigo-400 to-blue-500 rounded-full text-white text-2xl font-bold mb-6">
                3
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Get Your Plan</h3>
              <p className="text-gray-600 text-lg">Receive a personalized learning roadmap with curated courses and timeline.</p>
            </div>
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="mb-20">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">
            Success Stories
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/50">
                <div className="flex items-center mb-6">
                  <img 
                    src={testimonial.avatar} 
                    alt={testimonial.name}
                    className="w-16 h-16 rounded-full object-cover mr-4"
                  />
                  <div>
                    <h4 className="font-bold text-gray-900">{testimonial.name}</h4>
                    <p className="text-purple-600 font-medium">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-600 italic leading-relaxed">"{testimonial.content}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* Final CTA Section */}
        <div className="text-center bg-gradient-to-r from-pink-500 to-purple-600 rounded-3xl p-12 text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to Accelerate Your Career?</h2>
          <p className="text-xl mb-8 opacity-90">Join thousands of professionals who've transformed their careers with SkillUp AI</p>
          
          <button
            onClick={onGetStarted}
            className="group px-10 py-4 text-xl font-bold bg-white text-purple-600 rounded-full shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center mx-auto gap-3"
          >
            Start Your Journey Now
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </button>
          
          <div className="flex items-center justify-center gap-6 mt-8 text-sm opacity-80">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <span>100% Free</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <span>No Registration</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <span>Instant Results</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;