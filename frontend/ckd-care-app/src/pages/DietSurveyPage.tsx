import { Soup, Coffee, Pizza, Leaf } from "lucide-react";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { Tag } from "../components/Tag";
import { TextInput } from "../components/TextInput";
import { BtnPrimary } from "../components/BtnPrimary";

export function DietSurveyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="09 · 식이 설문 (REQ-DATA-05)" />
      <TopNav />
      <main className="flex flex-1 flex-col items-center p-[32px]">
        {/* 제목 */}
        <h1 className="text-2xl font-bold text-text-primary">
          간단 식이 설문
        </h1>

        {/* 정보 박스 */}
        <div className="mt-[16px] w-[640px] rounded-sm bg-bg-alt border border-border p-[12px]">
          <p className="text-xs text-text-secondary">
            이 설문은 LLM 컨텍스트 전용이며 예측 모델에는 직접 사용되지 않습니다.
            식이 패턴을 파악해 맞춤 챌린지 생성에 활용합니다.
          </p>
        </div>

        {/* 질문 카드들 */}
        <div className="mt-[24px] flex w-[640px] flex-col gap-[16px]">
          {/* Q1: 국·찌개 */}
          <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            <div className="flex items-center gap-[12px]">
              <Soup size={24} className="text-text-secondary" />
              <p className="flex-1 text-sm font-bold text-text-primary">
                하루 국·찌개·탕류를 몇 번 드시나요?
              </p>
              <Tag label="나트륨" />
            </div>
            <TextInput placeholder="예: 2회" />
          </div>

          {/* Q2: 단 음료 */}
          <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            <div className="flex items-center gap-[12px]">
              <Coffee size={24} className="text-text-secondary" />
              <p className="flex-1 text-sm font-bold text-text-primary">
                하루 단 음료 (커피 포함)를 몇 잔 드시나요?
              </p>
              <Tag label="당류" />
            </div>
            <TextInput placeholder="예: 3잔" />
          </div>

          {/* Q3: 튀긴 음식 */}
          <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            <div className="flex items-center gap-[12px]">
              <Pizza size={24} className="text-text-secondary" />
              <p className="flex-1 text-sm font-bold text-text-primary">
                주 몇 회 튀긴 음식을 드시나요?
              </p>
              <Tag label="지방" />
            </div>
            <TextInput placeholder="예: 주 3회" />
          </div>

          {/* Q4: 채소 */}
          <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            <div className="flex items-center gap-[12px]">
              <Leaf size={24} className="text-text-secondary" />
              <p className="flex-1 text-sm font-bold text-text-primary">
                매 끼 채소 반찬을 드시나요?
              </p>
              <Tag label="식이섬유" />
            </div>
            <div className="flex gap-[12px]">
              <button className="flex-1 rounded-md border border-border-strong bg-bg px-[16px] py-[10px] text-sm text-text-primary">
                예
              </button>
              <button className="flex-1 rounded-md border border-border-strong bg-bg px-[16px] py-[10px] text-sm text-text-primary">
                아니오
              </button>
            </div>
          </div>
        </div>

        {/* 완료 버튼 */}
        <div className="mt-[24px] w-[640px]">
          <BtnPrimary label="완료" height={48} className="w-full" />
        </div>
      </main>
    </div>
  );
}
