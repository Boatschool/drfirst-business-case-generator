import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Stack,
  Alert,
  Fab,
  Collapse,
  Divider,
  Badge,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Send as SendIcon,
  Close as CloseIcon,
  Minimize as MinimizeIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

interface AgentUpdate {
  timestamp: string;
  source: string;
  content: string;
}

interface FloatingChatProps {
  messages: AgentUpdate[];
  onSendMessage: (message: string) => Promise<void>;
  isSending: boolean;
  isLoading: boolean;
  error?: string;
  disabled?: boolean;
  currentCaseTitle?: string;
}

const FloatingChat: React.FC<FloatingChatProps> = ({
  messages,
  onSendMessage,
  isSending,
  isLoading,
  error,
  disabled = false,
  currentCaseTitle,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Count unread messages when chat is closed
  useEffect(() => {
    if (!isOpen) {
      // Simple logic: assume any new messages are unread when chat is closed
      const recentMessages = messages.filter((msg) => {
        const msgTime = new Date(msg.timestamp).getTime();
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
        return msgTime > fiveMinutesAgo && msg.source !== 'USER';
      });
      setUnreadCount(recentMessages.length);
    } else {
      setUnreadCount(0);
    }
  }, [messages, isOpen]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && chatInputRef.current) {
      setTimeout(() => chatInputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleToggleChat = () => {
    setIsOpen(!isOpen);
    setUnreadCount(0);
  };

  const handleSendMessage = async () => {
    if (!message.trim() || isSending || disabled) return;

    try {
      await onSendMessage(message);
      setMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Container */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 1000,
          width: isOpen ? 500 : 'auto',
          height: isOpen ? 500 : 'auto',
          transition: 'all 0.3s ease-in-out',
        }}
      >
        <Collapse in={isOpen} timeout={300}>
          <Paper
            elevation={8}
            sx={{
              width: 500,
              height: 500,
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 2,
              overflow: 'hidden',
              border: '1px solid #e0e0e0',
            }}
          >
            {/* Chat Header */}
            <Box
              sx={{
                backgroundColor: 'primary.main',
                color: 'primary.contrastText',
                p: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Stack
                direction="row"
                alignItems="center"
                spacing={1}
                sx={{ flex: 1, minWidth: 0 }}
              >
                <BotIcon />
                <Box sx={{ minWidth: 0, flex: 1 }}>
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: 600, fontSize: '1rem' }}
                  >
                    Agent Chat
                  </Typography>
                  {currentCaseTitle && (
                    <Typography
                      variant="caption"
                      sx={{
                        opacity: 0.9,
                        fontSize: '0.75rem',
                        display: 'block',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {currentCaseTitle}
                    </Typography>
                  )}
                </Box>
              </Stack>
              <Stack direction="row" spacing={0.5}>
                <IconButton
                  size="small"
                  onClick={handleToggleChat}
                  sx={{ color: 'primary.contrastText' }}
                >
                  <MinimizeIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={handleToggleChat}
                  sx={{ color: 'primary.contrastText' }}
                >
                  <CloseIcon />
                </IconButton>
              </Stack>
            </Box>

            {/* Messages Area */}
            <Box
              sx={{
                flex: 1,
                overflowY: 'auto',
                p: 1,
                backgroundColor: '#f8f9fa',
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
              }}
            >
              {messages.length > 0 ? (
                messages.map((msg, index) => (
                  <Box
                    key={`${msg.timestamp}-${index}`}
                    sx={{
                      alignSelf:
                        msg.source === 'USER' ? 'flex-end' : 'flex-start',
                      maxWidth: '75%',
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        backgroundColor:
                          msg.source === 'USER'
                            ? 'primary.main'
                            : 'background.paper',
                        color:
                          msg.source === 'USER'
                            ? 'primary.contrastText'
                            : 'text.primary',
                        borderRadius: 2,
                        wordBreak: 'break-word',
                      }}
                    >
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="flex-start"
                        sx={{ mb: 0.5 }}
                      >
                        {msg.source === 'USER' ? (
                          <PersonIcon sx={{ fontSize: 16, mt: 0.5 }} />
                        ) : (
                          <BotIcon sx={{ fontSize: 16, mt: 0.5 }} />
                        )}
                        <Box sx={{ flex: 1 }}>
                          <Typography
                            variant="caption"
                            display="block"
                            sx={{ opacity: 0.8, fontSize: '0.7rem' }}
                          >
                            {new Date(msg.timestamp).toLocaleTimeString()}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}
                          >
                            {msg.content}
                          </Typography>
                        </Box>
                      </Stack>
                    </Paper>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <BotIcon
                    sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }}
                  />
                  <Typography color="text.secondary" variant="body2">
                    {disabled
                      ? 'Navigate to a specific business case to start chatting with the agent'
                      : 'Start a conversation with the agent'}
                  </Typography>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>

            <Divider />

            {/* Input Area */}
            <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
              {error && (
                <Alert severity="error" sx={{ mb: 1, fontSize: '0.8rem' }}>
                  {error}
                </Alert>
              )}
              <Stack direction="row" spacing={1} alignItems="flex-end">
                <TextField
                  ref={chatInputRef}
                  fullWidth
                  size="small"
                  placeholder={
                    disabled
                      ? 'Select a business case to chat...'
                      : 'Type your message...'
                  }
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isSending || isLoading || disabled}
                  multiline
                  maxRows={3}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    },
                  }}
                />
                <IconButton
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={
                    !message.trim() || isSending || isLoading || disabled
                  }
                  sx={{
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '&:disabled': {
                      backgroundColor: 'action.disabled',
                    },
                  }}
                >
                  <SendIcon />
                </IconButton>
              </Stack>
              {(isSending || isLoading) && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mt: 0.5, display: 'block' }}
                >
                  {isSending ? 'Sending message...' : 'Processing...'}
                </Typography>
              )}
            </Box>
          </Paper>
        </Collapse>

        {/* Floating Action Button */}
        {!isOpen && (
          <Badge
            badgeContent={unreadCount}
            color="error"
            max={9}
            sx={{
              '& .MuiBadge-badge': {
                right: 8,
                top: 8,
              },
            }}
          >
            <Fab
              color="primary"
              onClick={handleToggleChat}
              disabled={disabled}
              sx={{
                width: 60,
                height: 60,
                boxShadow: 3,
                '&:hover': {
                  boxShadow: 6,
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <ChatIcon sx={{ fontSize: 28 }} />
            </Fab>
          </Badge>
        )}
      </Box>
    </>
  );
};

export default FloatingChat;
