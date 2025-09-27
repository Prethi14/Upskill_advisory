#!/usr/bin/env python3
"""
Test your specific Ollama models: llama3.2:1b and nomic-embed-text
"""

import requests
import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

class OllamaProjectTester:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
        # Get models from environment
        self.chat_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        
        print(f"Chat Model: {self.chat_model}")
        print(f"Embedding Model: {self.embedding_model}")
    
    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        print("\n1. Checking Ollama Service Status...")
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"   ✅ Ollama is running (version: {version_info.get('version', 'unknown')})")
                return True
            else:
                print(f"   ❌ Ollama returned status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("   ❌ Ollama is not running")
            print("   Start with: ollama serve")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def get_installed_models(self) -> List[str]:
        """Get list of installed models."""
        print("\n2. Checking Installed Models...")
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]
                print(f"   Found {len(models)} installed models:")
                for model in models:
                    print(f"     - {model}")
                return models
            else:
                print(f"   ❌ Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ Error getting models: {e}")
            return []
    
    def check_model_availability(self, model_name: str, installed_models: List[str]) -> bool:
        """Check if a specific model is available."""
        # Check exact match or partial match
        exact_match = model_name in installed_models
        partial_matches = [m for m in installed_models if model_name.split(':')[0] in m]
        
        if exact_match:
            print(f"   ✅ {model_name} is installed")
            return True
        elif partial_matches:
            print(f"   ⚠️  {model_name} not found, but similar models available: {partial_matches}")
            print(f"   You might want to update your .env to use: {partial_matches[0]}")
            return False
        else:
            print(f"   ❌ {model_name} is not installed")
            print(f"      Install with: ollama pull {model_name}")
            return False
    
    def test_chat_model(self) -> Dict[str, Any]:
        """Test the chat model with a simple prompt."""
        print(f"\n3. Testing Chat Model: {self.chat_model}")
        
        try:
            payload = {
                "model": self.chat_model,
                "prompt": "Hello! Please respond with just 'Chat model working' and nothing else.",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 10
                }
            }
            
            print("   Sending test prompt...")
            response = requests.post(f"{self.api_url}/generate", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                print(f"   ✅ Chat model response: {response_text}")
                
                # Show performance stats
                if "eval_duration" in result:
                    duration_sec = result["eval_duration"] / 1_000_000_000
                    tokens = result.get("eval_count", 0)
                    print(f"   Performance: {tokens} tokens in {duration_sec:.2f}s")
                
                return {"status": "success", "response": response_text}
            else:
                print(f"   ❌ Chat test failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            print(f"   ❌ Chat test error: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_embedding_model(self) -> Dict[str, Any]:
        """Test embedding models - try configured model first, then alternatives."""
        print(f"\n4. Testing Embedding Model: {self.embedding_model}")
        
        # Better alternative embedding models with known compatibility
        alternative_models = [
            "nomic-embed-text",
            "mxbai-embed-large", 
            "all-minilm",
            "snowflake-arctic-embed",
            "bge-large"
        ]
        
        test_text = "This is a test sentence for embeddings"
        
        def try_embedding_model(model_name: str) -> Dict[str, Any]:
            try:
                payload = {
                    "model": model_name,
                    "prompt": test_text
                }
                
                print(f"   Testing {model_name}...")
                response = requests.post(f"{self.api_url}/embeddings", json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    
                    if embedding and isinstance(embedding, list) and len(embedding) > 0:
                        print(f"   SUCCESS: {model_name} working")
                        print(f"   Embedding dimensions: {len(embedding)}")
                        print(f"   Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[-1]:.4f}]")
                        return {"status": "success", "dimensions": len(embedding), "model_used": model_name}
                    else:
                        print(f"   FAILED: {model_name} - No valid embedding returned")
                        return {"status": "error", "error": "No embedding in response"}
                        
                elif response.status_code == 404:
                    print(f"   NOT FOUND: {model_name} not installed")
                    print(f"      Install with: ollama pull {model_name}")
                    return {"status": "not_installed", "error": "Model not installed"}
                    
                else:
                    error_msg = response.text
                    print(f"   FAILED: {model_name} - Status {response.status_code}")
                    print(f"      Error: {error_msg}")
                    return {"status": "error", "error": error_msg}
                    
            except requests.exceptions.Timeout:
                print(f"   TIMEOUT: {model_name} - Request timed out (model might be loading)")
                return {"status": "timeout", "error": "Request timeout"}
                
            except Exception as e:
                print(f"   ERROR: {model_name} - {str(e)}")
                return {"status": "error", "error": str(e)}
        
        # Get list of installed models to check what's available
        print("\n   Checking installed models...")
        installed_models = self.get_installed_models()
        
        # Filter alternatives to only installed models
        available_models = []
        for model in alternative_models:
            if any(model in installed for installed in installed_models):
                available_models.append(model)
        
        print(f"   Found {len(available_models)} embedding models installed: {available_models}")
        
        # Start with configured model if it's installed
        models_to_try = []
        if self.embedding_model in available_models or any(self.embedding_model in installed for installed in installed_models):
            models_to_try.append(self.embedding_model)
        
        # Add other available models
        for model in available_models:
            if model != self.embedding_model:
                models_to_try.append(model)
        
        if not models_to_try:
            print(f"\n   NO EMBEDDING MODELS INSTALLED")
            print(f"   Install one of these recommended models:")
            print(f"   1. ollama pull mxbai-embed-large    (Recommended - reliable)")
            print(f"   2. ollama pull all-minilm           (Smaller, faster)")  
            print(f"   3. ollama pull nomic-embed-text     (Original choice)")
            return {"status": "error", "error": "No embedding models installed"}
        
        # Try each available model until one works
        print(f"\n   Trying {len(models_to_try)} available models...")
        for model in models_to_try:
            result = try_embedding_model(model)
            
            if result["status"] == "success":
                if model != self.embedding_model:
                    print(f"\n   RECOMMENDATION: Update your .env file:")
                    print(f"   OLLAMA_EMBEDDING_MODEL={model}")
                return result
        
        # If we get here, no models worked
        print(f"\n   ALL MODELS FAILED")
        print(f"   Try these solutions:")
        print(f"   1. Reinstall embedding models:")
        for model in models_to_try[:2]:  # Show first 2 failed models
            print(f"      ollama pull {model}")
        print(f"   2. Check Ollama logs: ollama logs")
        print(f"   3. Restart Ollama: kill ollama process, then 'ollama serve'")
        
        return {"status": "error", "error": "All embedding models failed"}
    
    def test_concurrent_usage(self) -> Dict[str, Any]:
        """Test both models working together."""
        print(f"\n5. Testing Concurrent Model Usage...")
        
        # First get an embedding
        embedding_result = self.test_embedding_model()
        if embedding_result["status"] != "success":
            print("   ❌ Skipping concurrent test - embedding model failed")
            return {"status": "skipped"}
        
        # Then do a chat completion
        chat_result = self.test_chat_model()
        if chat_result["status"] != "success":
            print("   ❌ Concurrent test failed - chat model failed")
            return {"status": "error"}
        
        print("   ✅ Both models working - ready for concurrent usage")
        return {"status": "success"}
    
    def run_full_test(self):
        """Run complete test suite for your project setup."""
        print("🔍 TESTING YOUR OLLAMA PROJECT SETUP")
        print("=" * 50)
        
        # Test 1: Service running
        if not self.check_ollama_running():
            print("\n❌ FAILED: Ollama is not running")
            print("Start Ollama with: ollama serve")
            return False
        
        # Test 2: Get installed models
        installed_models = self.get_installed_models()
        if not installed_models:
            print("\n❌ FAILED: No models installed")
            return False
        
        # Test 3: Check required models
        print("\n3. Checking Required Models...")
        chat_available = self.check_model_availability(self.chat_model, installed_models)
        embedding_available = self.check_model_availability(self.embedding_model, installed_models)
        
        missing_models = []
        
        if not chat_available:
            missing_models.append(f"Chat model: {self.chat_model}")
        
        if not embedding_available:
            missing_models.append(f"Embedding model: {self.embedding_model}")
        
        # Test 4: Functional tests (even with missing models, try to find alternatives)
        chat_result = None
        embedding_result = None
        
        if chat_available:
            chat_result = self.test_chat_model()
        
        # Always try embedding test (it will find alternatives if main model fails)
        embedding_result = self.test_embedding_model()
        
        # Evaluate results
        chat_working = chat_result and chat_result["status"] == "success"
        embedding_working = embedding_result and embedding_result["status"] == "success"
        
        print(f"\n6. Test Results Summary:")
        print(f"   Chat model: {'✅ Working' if chat_working else '❌ Failed'}")
        print(f"   Embedding model: {'✅ Working' if embedding_working else '❌ Failed'}")
        
        if embedding_working and embedding_result.get("model_used") != self.embedding_model:
            print(f"   Note: Using alternative embedding model: {embedding_result.get('model_used')}")
        
        # Determine overall status
        if chat_working and embedding_working:
            print("\n" + "=" * 50)
            print("🎉 SUCCESS: Your Ollama setup is working!")
            
            if chat_result["status"] == "success":
                print(f"✅ Chat model ({self.chat_model}) working")
            
            if embedding_result.get("model_used") == self.embedding_model:
                print(f"✅ Embedding model ({self.embedding_model}) working")
            else:
                print(f"✅ Embedding model ({embedding_result.get('model_used')}) working as alternative")
                print(f"   Consider updating .env: OLLAMA_EMBEDDING_MODEL={embedding_result.get('model_used')}")
            
            print("\nYour project can now use Ollama for:")
            print("- Text generation and chat")
            print("- Text embeddings for search/similarity")
            return True
        
        else:
            print("\n" + "=" * 50)
            print("⚠️  PARTIAL SUCCESS / ISSUES DETECTED")
            
            if missing_models:
                print("\nMissing models:")
                for model in missing_models:
                    print(f"  - {model}")
            
            if not chat_working and not embedding_working:
                print("\n❌ CRITICAL: Both models failed")
                print("Your project will not work properly without these models.")
            elif not chat_working:
                print("\n⚠️  Chat model not working - install and configure it")
            elif not embedding_working:
                print("\n⚠️  No embedding model working - try alternatives")
            
            print("\n🔧 RECOMMENDED ACTIONS:")
            if not chat_working:
                print(f"1. Install chat model: ollama pull {self.chat_model}")
            if not embedding_working:
                print("2. Install a working embedding model:")
                print("   ollama pull mxbai-embed-large")
                print("   OR ollama pull all-minilm")
                print("3. Update your .env file with working model name")
            
            return False

def check_environment_setup():
    """Check if environment variables are set correctly."""
    print("🔧 Environment Configuration:")
    print("-" * 30)
    
    chat_model = os.getenv("OLLAMA_MODEL")
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL")
    
    if chat_model:
        print(f"OLLAMA_MODEL: {chat_model}")
    else:
        print("❌ OLLAMA_MODEL not set in environment")
    
    if embedding_model:
        print(f"OLLAMA_EMBEDDING_MODEL: {embedding_model}")
    else:
        print("❌ OLLAMA_EMBEDDING_MODEL not set in environment")
    
    if not (chat_model and embedding_model):
        print("\nAdd these to your .env file:")
        print("OLLAMA_MODEL=llama3.2:1b")
        print("OLLAMA_EMBEDDING_MODEL=nomic-embed-text")

def quick_embedding_diagnostic():
    """Quick diagnostic to see what's wrong with embedding models."""
    print("QUICK EMBEDDING DIAGNOSTIC")
    print("=" * 40)
    
    base_url = "http://localhost:11434"
    
    # Check if Ollama is running
    try:
        response = requests.get(f"{base_url}/api/version", timeout=5)
        print("Ollama service: RUNNING")
    except:
        print("Ollama service: NOT RUNNING")
        print("Fix: Run 'ollama serve'")
        return
    
    # Get installed models
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            models = [model["name"] for model in models_data.get("models", [])]
            print(f"Installed models ({len(models)}): {models}")
        else:
            print("Could not get model list")
            return
    except Exception as e:
        print(f"Error getting models: {e}")
        return
    
    # Test embedding endpoint with each model
    print("\nTesting embedding endpoint:")
    embedding_models = [m for m in models if any(keyword in m.lower() for keyword in ['embed', 'minilm', 'nomic', 'bge', 'arctic'])]
    
    if not embedding_models:
        print("NO EMBEDDING MODELS FOUND")
        print("Install one: ollama pull mxbai-embed-large")
        return
    
    for model in embedding_models:
        try:
            payload = {"model": model, "prompt": "test"}
            response = requests.post(f"{base_url}/api/embeddings", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", [])
                if embedding:
                    print(f"  {model}: WORKING ({len(embedding)} dims)")
                else:
                    print(f"  {model}: NO EMBEDDING RETURNED")
            else:
                print(f"  {model}: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"  {model}: ERROR - {str(e)}")

def main():
    # Check environment first
    check_environment_setup()
    
    # Run quick diagnostic first
    print("\n")
    quick_embedding_diagnostic()
    
    # Ask user if they want to continue with full test
    print("\n" + "=" * 50)
    try:
        continue_test = input("Run full test? (y/n): ").lower().strip()
        if continue_test != 'y':
            print("Exiting. Run individual commands shown above to fix issues.")
            return
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    # Run full tests
    tester = OllamaProjectTester()
    success = tester.run_full_test()
    
    if not success:
        print("\nUse the quick diagnostic above to identify specific issues.")

if __name__ == "__main__":
    main()