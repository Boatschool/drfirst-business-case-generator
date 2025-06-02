import React, { createContext, useContext, useState, ReactNode, useCallback, useEffect } from 'react';
import {
  AgentService,
  InitiateCasePayload,
  InitiateCaseResponse,
  ProvideFeedbackPayload,
  AgentUpdate,
  BusinessCaseSummary,
  BusinessCaseDetails,
} from '../services/agent/AgentService';
import { HttpAgentAdapter } from '../services/agent/HttpAgentAdapter'; // Concrete implementation

interface AgentContextState {
  currentCaseId: string | null;
  messages: AgentUpdate[];
  cases: BusinessCaseSummary[];
  currentCaseDetails: BusinessCaseDetails | null;
  isLoading: boolean;
  isLoadingCases: boolean;
  isLoadingCaseDetails: boolean;
  error: Error | null;
  casesError: Error | null;
  caseDetailsError: Error | null;
}

interface AgentContextType extends AgentContextState {
  initiateBusinessCase: (payload: InitiateCasePayload) => Promise<InitiateCaseResponse | undefined>;
  sendFeedbackToAgent: (payload: ProvideFeedbackPayload) => Promise<void>;
  fetchUserCases: () => Promise<void>;
  fetchCaseDetails: (caseId: string) => Promise<void>;
  clearAgentState: () => void;
  clearCurrentCaseDetails: () => void;
  // TODO: Add a way to subscribe to agent updates via onAgentUpdate from AgentService
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

// Initialize the agent service instance. This could also be provided via props or another context if needed.
const agentService: AgentService = new HttpAgentAdapter();

interface AgentProviderProps {
  children: ReactNode;
}

export const AgentProvider: React.FC<AgentProviderProps> = ({ children }) => {
  const [state, setState] = useState<AgentContextState>({
    currentCaseId: null,
    messages: [],
    cases: [],
    currentCaseDetails: null,
    isLoading: false,
    isLoadingCases: false,
    isLoadingCaseDetails: false,
    error: null,
    casesError: null,
    caseDetailsError: null,
  });

  const fetchUserCases = useCallback(async () => {
    setState(prevState => ({ ...prevState, isLoadingCases: true, casesError: null }));
    try {
      const userCases = await agentService.listCases();
      setState(prevState => ({
        ...prevState,
        cases: userCases,
        isLoadingCases: false,
      }));
    } catch (err: any) {
      setState(prevState => ({ ...prevState, isLoadingCases: false, casesError: err }));
    }
  }, []);

  const initiateBusinessCase = useCallback(async (payload: InitiateCasePayload): Promise<InitiateCaseResponse | undefined> => {
    setState(prevState => ({ ...prevState, isLoading: true, error: null }));
    try {
      const response = await agentService.initiateCase(payload);
      setState(prevState => ({
        ...prevState,
        isLoading: false,
        currentCaseId: response.caseId,
        messages: response.initialMessage ? [
          {
            caseId: response.caseId,
            timestamp: new Date().toISOString(),
            source: 'AGENT', 
            messageType: 'TEXT',
            content: response.initialMessage,
          }
        ] : [],
      }));
      fetchUserCases();
      return response;
    } catch (err: any) {
      setState(prevState => ({ ...prevState, isLoading: false, error: err }));
      return undefined;
    }
  }, [fetchUserCases]);

  const fetchCaseDetails = useCallback(async (caseId: string) => {
    setState(prevState => ({ ...prevState, isLoadingCaseDetails: true, caseDetailsError: null, currentCaseDetails: null }));
    try {
      const details = await agentService.getCaseDetails(caseId);
      setState(prevState => ({
        ...prevState,
        currentCaseDetails: details,
        currentCaseId: caseId,
        messages: details.history || [],
        isLoadingCaseDetails: false,
      }));
    } catch (err: any) {
      setState(prevState => ({ ...prevState, isLoadingCaseDetails: false, caseDetailsError: err }));
    }
  }, []);
  
  const clearCurrentCaseDetails = useCallback(() => {
    setState(prevState => ({
      ...prevState,
      currentCaseDetails: null,
      messages: [],
      caseDetailsError: null,
    }));
  }, []);

  const clearAgentState = useCallback(() => {
    setState({
      currentCaseId: null,
      messages: [],
      cases: [],
      currentCaseDetails: null,
      isLoading: false,
      isLoadingCases: false,
      isLoadingCaseDetails: false,
      error: null,
      casesError: null,
      caseDetailsError: null,
    });
  }, []);
  
  // TODO: Implement effect for agentService.onAgentUpdate when currentCaseId is active
  // This effect would subscribe to updates and append them to the messages array.

  const value = {
    ...state,
    initiateBusinessCase,
    sendFeedbackToAgent: async (payload: ProvideFeedbackPayload) => {
      setState(prevState => ({ ...prevState, isLoading: true, error: null }));
      try {
        const userMessage: AgentUpdate = {
          caseId: payload.caseId,
          timestamp: new Date().toISOString(),
          source: 'USER',
          messageType: 'TEXT',
          content: payload.message, 
        };
        setState(prevState => ({
          ...prevState,
          messages: [...prevState.messages, userMessage],
        }));

        await agentService.provideFeedback(payload);
        setState(prevState => ({ ...prevState, isLoading: false }));
        
        if (state.currentCaseId === payload.caseId && state.currentCaseDetails) {
          fetchCaseDetails(payload.caseId);
        }
      } catch (err: any) {
        setState(prevState => ({ ...prevState, isLoading: false, error: err }));
      }
    },
    fetchUserCases,
    fetchCaseDetails,
    clearAgentState,
    clearCurrentCaseDetails,
  };

  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
};

export const useAgentContext = (): AgentContextType => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}; 