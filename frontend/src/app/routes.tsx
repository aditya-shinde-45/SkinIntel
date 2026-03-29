import { createBrowserRouter } from "react-router";
import { LandingPage } from "./pages/landing-page";
import { LoginPage } from "./pages/login-page";
import { SignupPage } from "./pages/signup-page";
import { AnalysisPage } from "./pages/analysis-page";
import { ResultPage } from "./pages/result-page";
import { ProtectedRoute } from "./components/protected-route";

export const router = createBrowserRouter([
  { path: "/",        Component: LandingPage },
  { path: "/login",   Component: LoginPage },
  { path: "/signup",  Component: SignupPage },
  {
    path: "/analyze",
    element: <ProtectedRoute><AnalysisPage /></ProtectedRoute>,
  },
  {
    path: "/results",
    element: <ProtectedRoute><ResultPage /></ProtectedRoute>,
  },
]);
