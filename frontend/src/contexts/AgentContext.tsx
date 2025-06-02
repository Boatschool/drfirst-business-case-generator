import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import {
  AgentService,
  InitiateCasePayload,
  InitiateCaseResponse,
  ProvideFeedbackPayload,
  AgentUpdate,
} from '../services/agent/AgentService';
import { HttpAgentAdapter } from '../services/agent/HttpAgentAdapter'; // Concrete implementation

interface AgentContextState {
  currentCaseId: string | null;
  messages: AgentUpdate[];
  isLoading: boolean;
  error: Error | null;
}

interface AgentContextType extends AgentContextState {
  initiateBusinessCase: (payload: InitiateCasePayload) => Promise<InitiateCaseResponse | undefined>;
  sendFeedbackToAgent: (payload: ProvideFeedbackPayload) => Promise<void>;
  clearAgentState: () => void;
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
    isLoading: false,
    error: null,
  });

  const initiateBusinessCase = useCallback(async (payload: InitiateCasePayload): Promise<InitiateCaseResponse | undefined> => {
    setState(prevState => ({ ...prevState, isLoading: true, error: null }));
    try {
      const response = await agentService.initiateCase(payload);
      setState(prevState => ({
        ...prevState,
        isLoading: false,
        currentCaseId: response.caseId,
        // Optionally add initial message from response if it exists
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
      return response;
    } catch (err: any) {
      setState(prevState => ({ ...prevState, isLoading: false, error: err }));
      return undefined;
    }
  }, []);

  const sendFeedbackToAgent = useCallback(async (payload: ProvideFeedbackPayload) => {
    setState(prevState => ({ ...prevState, isLoading: true, error: null }));
    try {
      // Add user message to local state immediately for better UX
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
      // Here, we might expect an update from the agent via onAgentUpdate
      // For now, the agent's response isn't automatically added after feedback
    } catch (err: any) {
      setState(prevState => ({ ...prevState, isLoading: false, error: err }));
    }
  }, []);

  const clearAgentState = useCallback(() => {
    setState({
      currentCaseId: null,
      messages: [],
      isLoading: false,
      error: null,
    });
  }, []);
  
  // TODO: Implement effect for agentService.onAgentUpdate when currentCaseId is active
  // This effect would subscribe to updates and append them to the messages array.

  const value = {
    ...state,
    initiateBusinessCase,
    sendFeedbackToAgent,
    clearAgentState,
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