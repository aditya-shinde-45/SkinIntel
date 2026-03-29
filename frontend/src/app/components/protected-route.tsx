import { Navigate } from 'react-router';
import { isLoggedIn } from '../utils/api';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
