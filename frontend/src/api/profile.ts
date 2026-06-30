import client from './client';
import type { StudentProfile } from '../types/profile';

export interface BuildProfileParams {
  message: string;
  subjectId?: string;
  sessionId?: string;
}

export async function buildProfile(params: BuildProfileParams): Promise<{ profile: StudentProfile }> {
  const { data } = await client.post('/api/profile/build', params);
  return data;
}

export async function getProfile(params: { sessionId: string; subjectId?: string }): Promise<{ profile: StudentProfile }> {
  const { data } = await client.get('/api/profile', { params });
  return data;
}

export async function updateProfile(updates: Partial<StudentProfile>): Promise<{ profile: StudentProfile }> {
  const { data } = await client.patch('/api/profile', updates);
  return data;
}
