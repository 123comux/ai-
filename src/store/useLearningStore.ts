import { create } from 'zustand';
import type { AbilityReport, LearningPath, Course, Project } from '@/types/index';

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
}

export const useLearningStore = create<LearningState>((set) => ({
  abilityReport: null,
  currentPath: null,
  courses: [],
  projects: [],
  learningDays: 0,
  totalHours: 0,
  completedProjects: 0,
  setAbilityReport: (report) => set({ abilityReport: report }),
  setCurrentPath: (path) => set({ currentPath: path }),
  setCourses: (courses) => set({ courses }),
  setProjects: (projects) => set({ projects }),
}));