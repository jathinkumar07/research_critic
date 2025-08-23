import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeDocument } from '../services/api';

const Home: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const validateFile = (file: File): string | null => {
    if (!file.type.includes('pdf')) {
      return 'Only PDF files are allowed';
    }
    if (file.size > 10 * 1024 * 1024) { // 10MB
      return 'File size must be less than 10MB';
    }
    return null;
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    setError(null);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      const selectedFile = droppedFiles[0];
      const validationError = validateFile(selectedFile);
      if (validationError) {
        setError(validationError);
        return;
      }
      setFile(selectedFile);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validationError = validateFile(selectedFile);
      if (validationError) {
        setError(validationError);
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const results = await analyzeDocument(file);
      // Store results in sessionStorage to pass to results page
      sessionStorage.setItem('analysisResults', JSON.stringify(results));
      navigate('/results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Research Critic
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            Upload your research document for comprehensive analysis including plagiarism detection, 
            citation validation, and fact-checking.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Drag and Drop Area */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 text-gray-400">
                <svg
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  className="w-full h-full"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {file ? file.name : 'Drop your PDF here'}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  or{' '}
                                     <label className="text-blue-600 hover:text-blue-500 cursor-pointer font-medium">
                    browse to upload
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      className="sr-only"
                    />
                  </label>
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  PDF files only, max 10MB
                </p>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* File Info */}
          {file && !error && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-800">
                    {file.name}
                  </p>
                  <p className="text-xs text-green-600">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-green-600 hover:text-green-800"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Analyze Button */}
          <div className="mt-8 text-center">
            <button
              onClick={handleAnalyze}
              disabled={!file || isLoading}
              className={`px-8 py-3 rounded-lg font-medium text-white transition-colors ${
                !file || isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Analyzing...
                </div>
              ) : (
                'Analyze Document'
              )}
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 text-blue-600">
              <svg fill="currentColor" viewBox="0 0 20 20" className="w-full h-full">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Plagiarism Detection
            </h3>
            <p className="text-gray-600">
              Advanced AI-powered plagiarism detection to ensure originality
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 text-blue-600">
              <svg fill="currentColor" viewBox="0 0 20 20" className="w-full h-full">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2v1a1 1 0 102 0V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 2a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Citation Analysis
            </h3>
            <p className="text-gray-600">
              Validate and analyze citations for accuracy and completeness
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 text-blue-600">
              <svg fill="currentColor" viewBox="0 0 20 20" className="w-full h-full">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Fact Checking
            </h3>
            <p className="text-gray-600">
              Verify claims and statements against reliable sources
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;