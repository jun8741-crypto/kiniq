import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { TextInput } from "../components/TextInput";
import { BtnPrimary } from "../components/BtnPrimary";
import { BtnSecondary } from "../components/BtnSecondary";

export function ManualInputPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="07 · 수동 입력 (REQ-DATA-03)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-text-primary">
            건강검진 수치 입력
          </h1>
          <TextInput
            label="검진일"
            placeholder="YYYY-MM-DD"
            className="w-[200px]"
          />
        </div>

        {/* 2칼럼 그리드 */}
        <div className="mt-[24px] grid grid-cols-2 gap-[32px]">
          {/* 좌측 칼럼 */}
          <div className="flex flex-col gap-[24px]">
            {/* 신체계측 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                신체계측
              </p>
              <div className="flex flex-col gap-[12px]">
                <TextInput label="신장 (cm)" placeholder="170.0" />
                <TextInput label="체중 (kg)" placeholder="72.5" />
                <TextInput label="BMI (kg/m2)" placeholder="자동 계산" />
                <TextInput label="허리둘레 (cm)" placeholder="85.0" />
              </div>
            </div>

            {/* 혈압 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                혈압
              </p>
              <div className="flex flex-col gap-[12px]">
                <TextInput
                  label="수축기 혈압 SBP (mmHg)"
                  placeholder="120"
                />
                <TextInput
                  label="이완기 혈압 DBP (mmHg)"
                  placeholder="80"
                />
              </div>
            </div>

            {/* CKD 마커 */}
            <div className="rounded-md border border-danger bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-danger">
                CKD 마커
              </p>
              <div className="flex flex-col gap-[12px]">
                <TextInput label="크레아티닌 (mg/dL)" placeholder="1.0" />
              </div>
            </div>
          </div>

          {/* 우측 칼럼 */}
          <div className="flex flex-col gap-[24px]">
            {/* 혈액검사 */}
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                혈액검사
              </p>
              <div className="flex flex-col gap-[12px]">
                <TextInput label="공복혈당 (mg/dL)" placeholder="100" />
                <TextInput label="중성지방 (mg/dL)" placeholder="150" />
                <TextInput label="HDL (mg/dL)" placeholder="60" />
                <TextInput label="LDL (mg/dL)" placeholder="100" />
                <TextInput label="AST (U/L)" placeholder="25" />
                <TextInput label="GOT (U/L)" placeholder="25" />
              </div>
            </div>

            {/* 정보 박스 */}
            <div className="rounded-sm bg-bg-alt p-[12px]">
              <p className="text-xs text-text-secondary">
                입력하신 수치는 CKD 위험도 예측 모델에 활용됩니다. 가능한 한
                최근 건강검진 결과를 정확히 입력해주세요.
              </p>
            </div>
          </div>
        </div>

        {/* 하단 버튼 */}
        <div className="mt-[32px] flex justify-end gap-[12px]">
          <BtnSecondary label="취소" />
          <BtnPrimary label="저장" />
        </div>
      </main>
    </div>
  );
}
