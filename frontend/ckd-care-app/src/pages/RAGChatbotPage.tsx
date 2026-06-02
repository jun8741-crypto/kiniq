import { Bot } from "lucide-react";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnPrimary } from "../components/BtnPrimary";

export function RAGChatbotPage() {
  return (
    <div className="flex h-screen flex-col bg-bg-alt">
      <ScreenLabel label="22 · RAG 챗봇 (P2, REQ-RAG-004/005 - KDIGO + 신장학회)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center gap-[12px] overflow-hidden p-[32px]">
        <div className="flex w-[760px] flex-1 flex-col rounded-md border border-border bg-bg">
          {/* 헤더 */}
          <div className="flex items-center gap-[12px] bg-bg-alt p-[12px]">
            <Bot size={24} className="text-accent" />
            <h2 className="text-md font-bold text-text-primary">
              신장 케어 AI 어시스턴트
            </h2>
          </div>

          {/* 채팅 영역 */}
          <div className="flex flex-1 flex-col gap-[12px] overflow-y-auto p-[16px]">
            {/* 유저 메시지 */}
            <div className="flex justify-end">
              <div className="rounded-md bg-accent p-[12px]">
                <p className="text-sm text-bg">
                  만성콩팥병 초기인데 어떤 음식을 피해야 하나요?
                </p>
              </div>
            </div>

            {/* AI 응답 */}
            <div className="flex gap-[8px]">
              <div className="h-[32px] w-[32px] shrink-0 rounded-full bg-accent" />
              <div className="flex flex-col gap-[8px] rounded-md bg-bg-alt p-[12px]">
                <p className="text-sm font-bold text-text-primary">
                  CKD 초기 식단 가이드
                </p>
                <p className="text-xs leading-[1.6] text-text-secondary">
                  만성콩팥병 초기(G1~G2)에서는 다음 식이 원칙이 권장됩니다:
                </p>
                <ul className="list-inside list-disc text-xs leading-[1.8] text-text-secondary">
                  <li>나트륨: 하루 2g 이하 (국·찌개 국물 절반 남기기)</li>
                  <li>단백질: 체중 kg당 0.8~1.0g (과다 섭취 주의)</li>
                  <li>칼륨: 바나나·감자·토마토 등 고칼륨 식품 제한</li>
                  <li>수분: 하루 1.5~2L 유지 (의사 권고량 우선)</li>
                </ul>
                <p className="text-xs text-text-muted">
                  출처: KDIGO 2024 CKD 가이드라인, 대한신장학회 식단 권고안
                </p>
              </div>
            </div>
          </div>

          {/* 입력 영역 */}
          <div className="flex gap-[8px] border-t border-border bg-bg p-[12px]">
            <div className="flex h-[40px] flex-1 items-center rounded-sm bg-bg-alt px-[12px] py-[8px]">
              <input
                type="text"
                placeholder="신장 건강에 대해 궁금한 것을 물어보세요 (Langfuse 트레이싱)"
                className="w-full bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
              />
            </div>
            <BtnPrimary label="전송" />
          </div>
        </div>
      </main>
    </div>
  );
}
