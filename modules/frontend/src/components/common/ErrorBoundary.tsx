import React, { Component, ReactNode } from 'react';
import { Result, Button, Typography, Space, Card, Alert } from 'antd';
import {
  ReloadOutlined,
  BugOutlined,
  HomeOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Paragraph, Text } = Typography;

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  errorCount: number;
}

/**
 * ErrorBoundary Component
 *
 * Catches JavaScript errors in child component tree and displays fallback UI.
 * Features:
 * - Automatic error recovery with reload
 * - Error logging to console (can be extended to backend)
 * - User-friendly error messages
 * - Development mode with stack trace
 * - Error count tracking to prevent infinite loops
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private errorLogTimeout: NodeJS.Timeout | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so next render shows fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error details
    console.error('ErrorBoundary caught an error:', error);
    console.error('Component stack:', errorInfo.componentStack);

    // Update state with error details
    this.setState(prevState => ({
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to backend (could be extended with API call)
    this.logErrorToService(error, errorInfo);

    // Auto-reload if too many errors (prevent infinite error loop)
    if (this.state.errorCount > 5) {
      console.warn('Too many errors detected, forcing page reload...');
      this.errorLogTimeout = setTimeout(() => {
        window.location.reload();
      }, 3000);
    }
  }

  componentWillUnmount(): void {
    if (this.errorLogTimeout) {
      clearTimeout(this.errorLogTimeout);
    }
  }

  private logErrorToService(error: Error, errorInfo: React.ErrorInfo): void {
    // TODO: Send to backend logging service
    const errorLog = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // For now, just log to console
    // In production, send to backend: POST /api/v1/logs/error
    console.log('Error logged:', errorLog);
  }

  private handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    });
  };

  private handleReload = (): void => {
    window.location.reload();
  };

  private handleGoHome = (): void => {
    window.location.href = '/';
  };

  render(): ReactNode {
    const { hasError, error, errorInfo, errorCount } = this.state;
    const { children, fallback, showDetails = process.env.NODE_ENV === 'development' } = this.props;

    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Show warning if too many errors
      const tooManyErrors = errorCount > 3;

      return (
        <div style={{
          padding: '50px 20px',
          maxWidth: '1200px',
          margin: '0 auto',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Card>
            <Result
              status="error"
              icon={<BugOutlined />}
              title="Si è verificato un errore"
              subTitle="Ci scusiamo per l'inconveniente. L'errore è stato registrato e verrà risolto al più presto."
              extra={
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space wrap>
                    <Button
                      type="primary"
                      icon={<ReloadOutlined />}
                      onClick={this.handleReset}
                      disabled={tooManyErrors}
                    >
                      Riprova
                    </Button>
                    <Button
                      icon={<ReloadOutlined />}
                      onClick={this.handleReload}
                    >
                      Ricarica Pagina
                    </Button>
                    <Button
                      icon={<HomeOutlined />}
                      onClick={this.handleGoHome}
                    >
                      Torna alla Home
                    </Button>
                  </Space>

                  {tooManyErrors && (
                    <Alert
                      message="Troppi errori rilevati"
                      description="Il sistema ha rilevato più errori consecutivi. Ricaricare la pagina o tornare alla home."
                      type="warning"
                      icon={<WarningOutlined />}
                      showIcon
                    />
                  )}
                </Space>
              }
            >
              {showDetails && error && (
                <Card
                  type="inner"
                  title="Dettagli Errore (Solo Sviluppo)"
                  style={{ marginTop: 20, textAlign: 'left' }}
                >
                  <Paragraph>
                    <Text strong>Messaggio:</Text>
                    <br />
                    <Text code>{error.message || 'Nessun messaggio'}</Text>
                  </Paragraph>

                  {error.stack && (
                    <Paragraph>
                      <Text strong>Stack Trace:</Text>
                      <pre style={{
                        backgroundColor: '#f5f5f5',
                        padding: 10,
                        borderRadius: 4,
                        overflow: 'auto',
                        maxHeight: 300,
                        fontSize: 12
                      }}>
                        {error.stack}
                      </pre>
                    </Paragraph>
                  )}

                  {errorInfo?.componentStack && (
                    <Paragraph>
                      <Text strong>Component Stack:</Text>
                      <pre style={{
                        backgroundColor: '#f5f5f5',
                        padding: 10,
                        borderRadius: 4,
                        overflow: 'auto',
                        maxHeight: 200,
                        fontSize: 12
                      }}>
                        {errorInfo.componentStack}
                      </pre>
                    </Paragraph>
                  )}

                  <Paragraph>
                    <Text type="secondary">
                      Errori consecutivi: {errorCount}
                    </Text>
                  </Paragraph>
                </Card>
              )}
            </Result>
          </Card>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
