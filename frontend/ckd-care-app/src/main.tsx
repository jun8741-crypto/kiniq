import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";

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

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/email-verify" element={<EmailVerifyPage />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/ocr-upload" element={<OCRUploadPage />} />
        <Route path="/ocr-result" element={<OCRResultPage />} />
        <Route path="/manual-input" element={<ManualInputPage />} />
        <Route path="/lifestyle-survey" element={<LifestyleSurveyPage />} />
        <Route path="/diet-survey" element={<DietSurveyPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/challenge" element={<ChallengeMainPage />} />
        <Route path="/daily-checkin" element={<DailyCheckinPage />} />
        <Route path="/egg-hatching" element={<EggHatchingPage />} />
        <Route path="/slump" element={<SlumpPage />} />
        <Route path="/llm-guide" element={<LLMActionGuidePage />} />
        <Route path="/notification-settings" element={<NotificationSettingsPage />} />
        <Route path="/notifications" element={<NotificationListPage />} />
        <Route path="/daily-quiz" element={<DailyQuizPage />} />
        <Route path="/social-group" element={<SocialGroupPage />} />
        <Route path="/family-cheer" element={<FamilyCheerPage />} />
        <Route path="/dining-mode" element={<DiningModePage />} />
        <Route path="/rag-chatbot" element={<RAGChatbotPage />} />
        <Route path="/simulation" element={<SimulationPage />} />
        <Route path="/checkup-history" element={<CheckupHistoryPage />} />
        <Route path="/emergency" element={<EmergencyGuardPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
