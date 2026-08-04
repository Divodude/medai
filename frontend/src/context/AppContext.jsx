import { createContext, useContext, useReducer, useEffect } from 'react';

const LS_SESSION_KEY = 'medai_session_id';
const LS_NAME_KEY    = 'medai_patient_name';

const initialState = {
  sessionId:    localStorage.getItem(LS_SESSION_KEY) || null,
  patientName:  localStorage.getItem(LS_NAME_KEY)    || 'Patient',
  analysis:     null,
  reportOpen:   false,
  messages:     [],
  loading:      false,
  loadingStage: '',
  sessions:     [],          // from GET /sessions
};

function reducer(state, action) {
  switch (action.type) {

    case 'SET_ANALYSIS':
      return {
        ...state,
        analysis:    action.payload.analysis,
        sessionId:   action.payload.sessionId,
        patientName: action.payload.patientName || state.patientName,
        loading:     false,
        loadingStage: '',
      };

    case 'TOGGLE_REPORT':
      return { ...state, reportOpen: !state.reportOpen };

    case 'OPEN_REPORT':
      return { ...state, reportOpen: true };

    case 'CLOSE_REPORT':
      return { ...state, reportOpen: false };

    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };

    // Append streamed chunk to last AI message
    case 'APPEND_AI_CHUNK': {
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === 'ai') {
        msgs[msgs.length - 1] = { ...last, content: last.content + action.payload, streaming: true };
      }
      return { ...state, messages: msgs };
    }

    case 'FINISH_STREAM': {
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === 'ai') {
        msgs[msgs.length - 1] = { ...last, streaming: false };
      }
      return { ...state, messages: msgs };
    }

    case 'SET_LOADING':
      return { ...state, loading: action.payload.loading, loadingStage: action.payload.stage || '' };

    case 'SET_SESSIONS':
      return { ...state, sessions: action.payload };

    case 'SWITCH_SESSION':
      return {
        ...state,
        sessionId:   action.payload.sessionId,
        patientName: action.payload.patientName,
        analysis:    action.payload.analysis || null,
        messages:    [],
        reportOpen:  false,
      };

    case 'NEW_SESSION':
      return {
        ...initialState,
        sessionId:   null,
        patientName: 'Patient',
        sessions:    state.sessions,
        messages:    [{ role: 'ai', content: 'Hello! Upload your medical report to get started. I can analyse it and answer your questions.', streaming: false }],
      };

    default:
      return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, {
    ...initialState,
    messages: [{ role: 'ai', content: 'Hello! Upload your medical report using the 📎 button below. I\'ll analyse it and answer all your questions.', streaming: false }],
  });

  // Persist session to localStorage whenever it changes
  useEffect(() => {
    if (state.sessionId) {
      localStorage.setItem(LS_SESSION_KEY, state.sessionId);
    } else {
      localStorage.removeItem(LS_SESSION_KEY);
    }
  }, [state.sessionId]);

  useEffect(() => {
    localStorage.setItem(LS_NAME_KEY, state.patientName);
  }, [state.patientName]);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}
