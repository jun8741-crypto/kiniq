import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./index.css";

import { AuthProvider, useAuth } from "./contexts/AuthContext";

import { LoginPage } from "./pages/LoginPage";
import { SignupPage } from "./pages/SignupPage";
import { EmailVerifyPage } from "./pages/EmailVerifyPage";
import { MyPage } from "./pages/MyPage";
import { OCRUploadPage } from "./pages/OCRUploadPage";
import { OCRResultPage } from "./pages/OCRResultPage";
import { ManualInputPage } from "./pages/ManualInputPage";
import { LifestyleSurveyPage } from "./pages/LifestyleSurveyPage";
import { DietSurveyPage } from "./pages/DietSurveyPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ChallengeMainPage } from "./pages/ChallengeMainPage";
import { DailyCheckinPage } from "./pages/DailyCheckinPage";
import { EggHatchingPage } from "./pages/EggHatchingPage";
import { SlumpPage } from "./pages/SlumpPage";
import { LLMActionGuidePage } from "./pages/LLMActionGuidePage";
import { NotificationSettingsPage } from "./pages/NotificationSettingsPage";
import { NotificationListPage } from "./pages/NotificationListPage";
import { DailyQuizPage } from "./pages/DailyQuizPage";
import { SocialGroupPage } from "./pages/SocialGroupPage";
import { FamilyCheerPage } from "./pages/FamilyCheerPage";
import { DiningModePage } from "./pages/DiningModePage";
import { RAGChatbotPage } from "./pages/RAGChatbotPage";
import { SimulationPage } from "./pages/SimulationPage";
import { CheckupHistoryPage } from "./pages/CheckupHistoryPage";
import { EmergencyGuardPage } from "./pages/EmergencyGuardPage";
import { OAuthCallbackPage } from "./pages/OAuthCallbackPage";
import { ShopPage } from "./pages/ShopPage";
import { PointHistoryPage } from "./pages/PointHistoryPage";
import { CollectionPage } from "./pages/CollectionPage";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token, isLoading } = useAuth();
  if (isLoading) return <div className="flex min-h-screen items-center justify-center text-text-secondary">로딩 중...</div>;
  return token ? <>{children}</> : <Navigate to="/" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* 공개 라우트 */}
      <Route path="/" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/email-verify" element={<EmailVerifyPage />} />
      <Route path="/oauth/callback" element={<OAuthCallbackPage />} />

      {/* 인증 필요 라우트 */}
      <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
      <Route path="/mypage" element={<PrivateRoute><MyPage /></PrivateRoute>} />
      <Route path="/ocr-upload" element={<PrivateRoute><OCRUploadPage /></PrivateRoute>} />
      <Route path="/ocr-result" element={<PrivateRoute><OCRResultPage /></PrivateRoute>} />
      <Route path="/manual-input" element={<PrivateRoute><ManualInputPage /></PrivateRoute>} />
      <Route path="/lifestyle-survey" element={<PrivateRoute><LifestyleSurveyPage /></PrivateRoute>} />
      <Route path="/diet-survey" element={<PrivateRoute><DietSurveyPage /></PrivateRoute>} />
      <Route path="/challenge" element={<PrivateRoute><ChallengeMainPage /></PrivateRoute>} />
      <Route path="/daily-checkin" element={<PrivateRoute><DailyCheckinPage /></PrivateRoute>} />
      <Route path="/egg-hatching" element={<PrivateRoute><EggHatchingPage /></PrivateRoute>} />
      <Route path="/slump" element={<PrivateRoute><SlumpPage /></PrivateRoute>} />
      <Route path="/llm-guide" element={<PrivateRoute><LLMActionGuidePage /></PrivateRoute>} />
      <Route path="/notification-settings" element={<PrivateRoute><NotificationSettingsPage /></PrivateRoute>} />
      <Route path="/notifications" element={<PrivateRoute><NotificationListPage /></PrivateRoute>} />
      <Route path="/daily-quiz" element={<PrivateRoute><DailyQuizPage /></PrivateRoute>} />
      <Route path="/social-group" element={<PrivateRoute><SocialGroupPage /></PrivateRoute>} />
      <Route path="/family-cheer" element={<PrivateRoute><FamilyCheerPage /></PrivateRoute>} />
      <Route path="/dining-mode" element={<PrivateRoute><DiningModePage /></PrivateRoute>} />
      <Route path="/rag-chatbot" element={<PrivateRoute><RAGChatbotPage /></PrivateRoute>} />
      <Route path="/simulation" element={<PrivateRoute><SimulationPage /></PrivateRoute>} />
      <Route path="/checkup-history" element={<PrivateRoute><CheckupHistoryPage /></PrivateRoute>} />
      <Route path="/health-check-history" element={<PrivateRoute><CheckupHistoryPage /></PrivateRoute>} />
      <Route path="/emergency" element={<PrivateRoute><EmergencyGuardPage /></PrivateRoute>} />
      <Route path="/shop" element={<PrivateRoute><ShopPage /></PrivateRoute>} />
      <Route path="/points/transactions" element={<PrivateRoute><PointHistoryPage /></PrivateRoute>} />
      <Route path="/collection" element={<PrivateRoute><CollectionPage /></PrivateRoute>} />
    </Routes>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
