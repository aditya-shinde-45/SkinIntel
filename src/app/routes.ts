import { createBrowserRouter } from "react-router";
import { LandingPage } from "./pages/landing-page";
import { LoginPage } from "./pages/login-page";
import { SignupPage } from "./pages/signup-page";
import { AnalysisPage } from "./pages/analysis-page";
import { ResultPage } from "./pages/result-page";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: LandingPage,
  },
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/signup",
    Component: SignupPage,
  },
  {
    path: "/analyze",
    Component: AnalysisPage,
  },
  {
    path: "/results",
    Component: ResultPage,
  },
]);
