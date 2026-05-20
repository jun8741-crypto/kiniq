import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { Tag } from "../components/Tag";
import { ChartPlaceholder } from "../components/ChartPlaceholder";
import { Card } from "../components/Card";

export function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="10 · 대시보드 (REQ-DASH-01)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">
        {/* 헤더 */}
        <div className="flex items-center gap-[12px]">
          <h1 className="text-2xl font-bold text-text-primary">
            안녕하세요, 홍길동 님
          </h1>
          <Tag label="G2 · 경계군" />
          <Tag label="A 트랙 · 스테이지 1" />
        </div>

        {/* Row1: 듀얼 계기판 + 헬스 알 */}
        <div className="mt-[24px] flex gap-[24px]">
          <div className="flex flex-1 gap-[16px]">
            <ChartPlaceholder
              title="eGFR 계기판"
              className="flex-1"
              height={200}
            />
            <ChartPlaceholder
              title="CKD 위험도"
              className="flex-1"
              height={200}
            />
          </div>
          <div className="flex w-[280px] flex-col items-center justify-center gap-[8px] rounded-md border border-border bg-bg p-[16px]">
            {/* 헬스 알 캐릭터 */}
            <div className="flex h-[120px] w-[100px] items-center justify-center rounded-full bg-success/20">
              <span className="text-3xl">🥚</span>
            </div>
            <p className="text-sm font-bold text-text-primary">나의 헬스 알</p>
            <p className="text-xs text-text-secondary">체력 82/100</p>
          </div>
        </div>

        {/* Row2: eGFR 추세 */}
        <div className="mt-[24px]">
          <ChartPlaceholder title="eGFR 추세 차트" height={240} />
        </div>

        {/* Row3: 챌린지 잔디 + SHAP */}
        <div className="mt-[24px] flex gap-[24px]">
          <ChartPlaceholder
            title="챌린지 잔디 히트맵"
            className="flex-1"
            height={180}
          />
          <ChartPlaceholder
            title="SHAP Top 5 기여 요인"
            className="flex-1"
            height={180}
          />
        </div>

        {/* Row4: 라디알 미니 5종 + 주간 달성 */}
        <div className="mt-[24px] flex gap-[24px]">
          <div className="flex flex-1 gap-[12px]">
            {["수분", "저염식", "운동", "수면", "스트레스"].map((name) => (
              <Card
                key={name}
                title={name}
                className="flex-1 items-center"
              >
                <div className="flex h-[60px] w-[60px] items-center justify-center rounded-full border-4 border-accent">
                  <span className="text-xs font-bold text-text-primary">
                    75%
                  </span>
                </div>
              </Card>
            ))}
          </div>
          <ChartPlaceholder
            title="주간 달성 차트"
            className="w-[320px]"
            height={160}
          />
        </div>

        {/* 면책 문구 */}
        <p className="mt-[24px] text-center text-xs text-text-muted">
          본 서비스는 의료 진단·처방을 대체하지 않습니다. 수치 해석은 담당
          의료진과 상의하세요.
        </p>
      </main>
    </div>
  );
}
