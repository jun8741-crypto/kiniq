import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { Checkbox } from "../components/Checkbox";
import { BtnPrimary } from "../components/BtnPrimary";

export function LifestyleSurveyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="08 · 생활습관 설문 (REQ-DATA-04)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">
        {/* 제목 */}
        <h1 className="text-2xl font-bold text-text-primary">생활습관 설문</h1>

        {/* 진행 바 */}
        <div className="mt-[16px] h-[8px] w-full rounded-full bg-placeholder">
          <div className="h-full w-[60%] rounded-full bg-accent" />
        </div>
        <p className="mt-[4px] text-xs text-text-muted">3 / 5 섹션 완료</p>

        {/* 2칼럼 */}
        <div className="mt-[24px] grid grid-cols-2 gap-[32px]">
          {/* 좌측 */}
          <div className="flex flex-col gap-[24px]">
            {/* 진단·가족력 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                진단·가족력
              </p>
              <div className="flex flex-col gap-[10px]">
                <Checkbox label="고혈압 진단" />
                <Checkbox label="당뇨병 진단" />
                <Checkbox label="이상지질혈증 진단" />
                <Checkbox label="심혈관 질환 가족력" />
                <Checkbox label="신장 질환 가족력" />
                <Checkbox label="기타 만성질환" />
              </div>
            </div>

            {/* 흡연·음주 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                흡연·음주
              </p>
              <div className="flex flex-col gap-[12px]">
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    흡연 상태
                  </label>
                  <div className="flex gap-[8px]">
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      비흡연
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      과거 흡연
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      현재 흡연
                    </button>
                  </div>
                </div>
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    음주 빈도
                  </label>
                  <div className="flex gap-[8px]">
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      안 마심
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      월 1~4회
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      주 2회+
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 우측 */}
          <div className="flex flex-col gap-[24px]">
            {/* 신체활동 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                신체활동
              </p>
              <div className="flex flex-col gap-[12px]">
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    주간 운동 빈도
                  </label>
                  <div className="flex gap-[8px]">
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      안 함
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      1~2회
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      3~4회
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      5회+
                    </button>
                  </div>
                </div>
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    1회 운동 시간
                  </label>
                  <div className="flex gap-[8px]">
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      30분 미만
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      30~60분
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      60분+
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* 결혼·기타 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                결혼·기타
              </p>
              <div className="flex flex-col gap-[12px]">
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    결혼 여부
                  </label>
                  <div className="flex gap-[8px]">
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      미혼
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      기혼
                    </button>
                    <button className="flex-1 rounded-sm border border-border-strong bg-bg px-[12px] py-[8px] text-sm text-text-primary">
                      기타
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 완료 버튼 */}
        <div className="mt-[32px] flex justify-end">
          <BtnPrimary label="설문 완료" />
        </div>
      </main>
    </div>
  );
}
