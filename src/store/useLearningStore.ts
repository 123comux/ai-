import { create } from 'zustand';
import type { AbilityReport, LearningPath, Course, Project } from '@/types/index';
import { mockAbilityReport } from '@/data/assessment';
import { mockLearningPath } from '@/data/learningPaths';
import { mockCourses } from '@/data/courses';
import { mockProjects } from '@/data/projects';

interface LearningState {
  abilityReport: AbilityReport | null;
  currentPath: LearningPath | null;
  courses: Course[];
  projects: Project[];
  learningDays: number;
  totalHours: number;
  completedProjects: number;
  setAbilityReport: (report: AbilityReport) => void;
  setCurrentPath: (path: LearningPath) => void;
  setCourses: (courses: Course[]) => void;
  setProjects: (projects: Project[]) => void;
  loadData: () => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  abilityReport: null,
  currentPath: null,
  courses: [],
  projects: [],
  learningDays: 15,
  totalHours: 48,
  completedProjects: 1,
  setAbilityReport: (report) => set({ abilityReport: report }),
  setCurrentPath: (path) => set({ currentPath: path }),
  setCourses: (courses) => set({ courses }),
  setProjects: (projects) => set({ projects }),
  loadData: () => set({
    abilityReport: mockAbilityReport,
    currentPath: mockLearningPath,
    courses: mockCourses,
    projects: mockProjects,
  }),
}));