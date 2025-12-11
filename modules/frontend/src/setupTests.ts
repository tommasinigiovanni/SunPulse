// Setup per Jest e React Testing Library
import '@testing-library/jest-dom';

// Mock per matchMedia (usato da Ant Design)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock per ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock per WebSocket
global.WebSocket = jest.fn().mockImplementation(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: WebSocket.OPEN,
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
}));

// Mock per console.error in test per evitare spam
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Mock per Auth0
jest.mock('@auth0/auth0-react', () => ({
  Auth0Provider: ({ children }: { children: React.ReactNode }) => children,
  useAuth0: () => ({
    isLoading: false,
    isAuthenticated: true,
    user: {
      sub: 'auth0|123456789',
      name: 'Test User',
      email: 'test@example.com',
      picture: 'https://example.com/avatar.jpg',
    },
    loginWithRedirect: jest.fn(),
    logout: jest.fn(),
    getAccessTokenSilently: jest.fn().mockResolvedValue('mock-token'),
  }),
}));

// Mock per React Query
jest.mock('@tanstack/react-query', () => ({
  ...jest.requireActual('@tanstack/react-query'),
  useQuery: jest.fn().mockReturnValue({
    data: null,
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
  useQueryClient: jest.fn().mockReturnValue({
    invalidateQueries: jest.fn(),
    setQueryData: jest.fn(),
    getQueryData: jest.fn(),
  }),
}));

// Mock per Chart components
jest.mock('@ant-design/charts', () => ({
  Line: () => <div data-testid="line-chart">Line Chart</div>,
  Column: () => <div data-testid="column-chart">Column Chart</div>,
  Area: () => <div data-testid="area-chart">Area Chart</div>,
  Pie: () => <div data-testid="pie-chart">Pie Chart</div>,
}));

// Utilities per test
export const mockDevice = {
  id: '1',
  name: 'Test Inverter',
  type: 'inverter' as const,
  status: 'online' as const,
  serial_number: 'TEST001',
  current_power: 1500,
  daily_energy: 12.5,
  total_energy: 5000,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockRealTimeData = {
  device_id: '1',
  timestamp: '2024-01-01T12:00:00Z',
  power: 1500,
  voltage: 220,
  current: 6.8,
  energy_today: 12.5,
  status: 'online' as const,
};

// Custom render per test con providers
import React from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import { BrowserRouter } from 'react-router-dom';

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
}

export function render(
  ui: React.ReactElement,
  {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    }),
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider>
          {children}
        </ConfigProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );

  return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
}

// Re-export everything
export * from '@testing-library/react'; 