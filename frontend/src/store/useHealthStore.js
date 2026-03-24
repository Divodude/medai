import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useHealthStore = create(
  persist(
    (set, get) => ({
      // Session
      sessionId: null,
      patientName: 'Patient',
      setSessionId: (id) => set({ sessionId: id }),
      setPatientName: (name) => set({ patientName: name }),

      // Analysis result
      analysisResult: null,
      isAnalyzing: false,
      setAnalysisResult: (result) => set({ analysisResult: result }),
      setIsAnalyzing: (val) => set({ isAnalyzing: val }),

      // Tracking: which exercises are done today
      completedExercises: {},
      toggleExercise: (name) =>
        set((state) => ({
          completedExercises: {
            ...state.completedExercises,
            [name]: !state.completedExercises[name],
          },
        })),

      // Tracking: which meals are logged today
      loggedMeals: {},
      toggleMeal: (name) =>
        set((state) => ({
          loggedMeals: {
            ...state.loggedMeals,
            [name]: !state.loggedMeals[name],
          },
        })),

      // Chat
      chatMessages: [],
      isChatOpen: false,
      isChatLoading: false,
      addChatMessage: (msg) =>
        set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
      setChatMessages: (msgsOrUpdater) =>
        set((state) => ({
          chatMessages: typeof msgsOrUpdater === 'function'
            ? msgsOrUpdater(state.chatMessages)
            : msgsOrUpdater,
        })),
      setIsChatOpen: (val) => set({ isChatOpen: val }),
      setIsChatLoading: (val) => set({ isChatLoading: val }),

      // Reset daily tracking
      resetTracking: () =>
        set({ completedExercises: {}, loggedMeals: {} }),

      // User location
      userLocation: '',
      setUserLocation: (loc) => set({ userLocation: loc }),
    }),
    {
      name: 'health-assistant-store',
      partialize: (state) => ({
        sessionId: state.sessionId,
        patientName: state.patientName,
        completedExercises: state.completedExercises,
        loggedMeals: state.loggedMeals,
        userLocation: state.userLocation,
      }),
    }
  )
);

export default useHealthStore;
