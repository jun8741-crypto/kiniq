import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { BtnPrimary } from "../components/BtnPrimary";
import { BtnSecondary } from "../components/BtnSecondary";

/* OCR 결과 데이터 */
const ocrRows = [
  { name: "신장 (cm)", value: "170.2", confidence: 97, low: false },
  { name: "체중 (kg)", value: "72.5", confidence: 95, low: false },
  { name: "공복혈당 (mg/dL)", value: "118", confidence: 72, low: true },
  { name: "수축기 혈압 (mmHg)", value: "128", confidence: 91, low: false },
  { name: "중성지방 (mg/dL)", value: "195", confidence: 68, low: true },
  { name: "크레아티닌 (mg/dL)", value: "1.12", confidence: 94, low: false },
];

export function OCRResultPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="06 · OCR 결과 (REQ-DATA-02)" />
      <TopNav />
      <main className="flex flex-1 flex-col items-center p-[32px]">
        {/* 헤더 */}
        <div className="flex w-[800px] items-center justify-between">
          <h1 className="text-2xl font-bold text-text-primary">
            OCR 추출 결과
          </h1>
          <span className="rounded-sm bg-warning/10 px-[10px] py-[4px] text-sm font-bold text-warning">
            &#9888; 신뢰도 낮은 항목 3개
          </span>
        </div>

        {/* 테이블 */}
        <div className="mt-[24px] w-[800px] overflow-hidden rounded-md border border-border bg-bg">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-bg-alt">
                <th className="px-[16px] py-[12px] text-left font-bold text-text-primary">
                  항목
                </th>
                <th className="px-[16px] py-[12px] text-left font-bold text-text-primary">
                  OCR 값
                </th>
                <th className="px-[16px] py-[12px] text-left font-bold text-text-primary">
                  신뢰도
                </th>
                <th className="px-[16px] py-[12px] text-left font-bold text-text-primary">
                  수동 보정
                </th>
              </tr>
            </thead>
            <tbody>
              {ocrRows.map((row) => (
                <tr
                  key={row.name}
                  className={`border-b border-border ${
                    row.low ? "border-t-2 border-t-warning bg-bg-alt" : ""
                  }`}
                >
                  <td className="px-[16px] py-[12px] text-text-primary">
                    {row.name}
                  </td>
                  <td className="px-[16px] py-[12px] text-text-primary">
                    {row.value}
                  </td>
                  <td className="px-[16px] py-[12px]">
                    <span
                      className={`font-bold ${
                        row.low ? "text-warning" : "text-success"
                      }`}
                    >
                      {row.confidence}%{row.low && " ⚠"}
                    </span>
                  </td>
                  <td className="px-[16px] py-[12px]">
                    {row.low ? (
                      <input
                        type="text"
                        placeholder="보정 값 입력"
                        className="h-[32px] w-[120px] rounded-sm border border-border-strong px-[8px] text-sm text-text-primary outline-none placeholder:text-text-muted"
                      />
                    ) : (
                      <span className="text-text-muted">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 추가 항목 안내 */}
        <p className="mt-[12px] w-[800px] text-sm text-text-muted">
          &hellip; 외 12개 항목
        </p>

        {/* 하단 버튼 */}
        <div className="mt-[24px] flex w-[800px] justify-end gap-[12px]">
          <BtnSecondary label="다시 업로드" />
          <BtnPrimary label="저장하고 예측 실행" />
        </div>
      </main>
    </div>
  );
}
