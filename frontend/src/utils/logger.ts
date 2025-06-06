/**
 * Logger utility for frontend development and debugging
 * Respects VITE_ENABLE_DEBUG_LOGGING environment variable
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerConfig {
  enableDebugLogging: boolean;
  prefix?: string;
}

class Logger {
  private config: LoggerConfig;

  constructor(config: Partial<LoggerConfig> = {}) {
    this.config = {
      enableDebugLogging: import.meta.env.VITE_ENABLE_DEBUG_LOGGING === 'true',
      ...config,
    };
  }

  private formatMessage(level: LogLevel, message: string, ...args: any[]): [string, ...any[]] {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    const prefix = this.config.prefix ? `[${this.config.prefix}]` : '';
    const levelEmoji = {
      debug: '🔍',
      info: 'ℹ️',
      warn: '⚠️',
      error: '❌',
    }[level];
    
    return [`${levelEmoji} ${timestamp} ${prefix} ${message}`, ...args];
  }

  /**
   * Debug logging - only appears when VITE_ENABLE_DEBUG_LOGGING=true
   */
  debug(message: string, ...args: any[]): void {
    if (this.config.enableDebugLogging) {
      console.debug(...this.formatMessage('debug', message, ...args));
    }
  }

  /**
   * Info logging - only appears when VITE_ENABLE_DEBUG_LOGGING=true
   */
  info(message: string, ...args: any[]): void {
    if (this.config.enableDebugLogging) {
      console.info(...this.formatMessage('info', message, ...args));
    }
  }

  /**
   * Warning logging - always appears (but can be disabled in production builds)
   */
  warn(message: string, ...args: any[]): void {
    console.warn(...this.formatMessage('warn', message, ...args));
  }

  /**
   * Error logging - always appears
   */
  error(message: string, ...args: any[]): void {
    console.error(...this.formatMessage('error', message, ...args));
  }

  /**
   * Create a logger with a specific prefix for a component/service
   */
  static create(prefix: string): Logger {
    return new Logger({ prefix });
  }
}

// Default logger instance
export const logger = new Logger();

// Named exports for convenience
export default Logger; 