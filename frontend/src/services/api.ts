import axios from 'axios';
import { AnalysisResponse, ApiError } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for analysis
});

export const analyzeDocument = async (file: File): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<AnalysisResponse>('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const errorData = error.response.data as ApiError;
      throw new Error(errorData.error || 'Analysis failed');
    }
    throw new Error('Network error occurred');
  }
};

export const healthCheck = async (): Promise<{ status: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend is not available');
  }
};