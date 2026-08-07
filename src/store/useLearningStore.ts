import { create } from 'zustand';
import type { AbilityReport, LearningPath, Course, Project } from '@/types/index';

interface LearningState {
  abilityReport: AbilityReport | null;
  currentPath: LearningPath | null;
  courses: Course[];
  projects: Project[];
  selectedTopic: string;  // 从首页选择的学习方向，用于学习页预过滤
  setAbilityReport: (report: AbilityReport) => void;
  setCurrentPath: (path: LearningPath) => void;
  setCourses: (courses: Course[]) => void;
  setProjects: (projects: Project[]) => void;
  setSelectedTopic: (topic: string) => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  abilityReport: null,
  currentPath: null,
  courses: [],
  projects: [],
  selectedTopic: 'all',
  setAbilityReport: (report) => set({ abilityReport: report }),
  setCurrentPath: (path) => set({ currentPath: path }),
  setCourses: (courses) => set({ courses }),
  setProjects: (projects) => set({ projects }),
  setSelectedTopic: (topic) => set({ selectedTopic: topic }),
}));