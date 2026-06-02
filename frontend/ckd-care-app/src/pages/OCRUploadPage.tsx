import { CloudUpload, Clock, Trash2, ShieldCheck } from "lucide-react";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { BtnPrimary } from "../components/BtnPrimary";

export function OCRUploadPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="05 · OCR 업로드 (REQ-DATA-01)" />
      <TopNav />
      <main className="flex flex-1 flex-col items-center p-[32px]">
        {/* 제목 */}
        <h1 className="text-2xl font-bold text-text-primary">
          건강검진 결과지 업로드
        </h1>
        <p className="mt-[8px] text-sm text-text-secondary">
          건강검진 결과지를 업로드하면 AI가 주요 수치를 자동으로 추출합니다.
        </p>

        {/* 드롭존 */}
        <div className="mt-[32px] flex h-[280px] w-[720px] flex-col items-center justify-center gap-[16px] rounded-lg border-2 border-dashed border-border-strong bg-bg">
          <CloudUpload size={48} className="text-text-muted" />
          <BtnPrimary label="파일 선택" />
          <p className="text-xs text-text-muted">
            PDF, JPG, PNG 형식 지원 · 최대 10MB
          </p>
        </div>

        {/* 정보 박스 */}
        <div className="mt-[24px] flex w-[720px] flex-col gap-[12px]">
          <div className="flex items-center gap-[8px]">
            <Clock size={16} className="shrink-0 text-text-secondary" />
            <p className="text-sm text-text-secondary">
              처리 시간: 약 10~30초 소요
            </p>
          </div>
          <div className="flex items-center gap-[8px]">
            <Trash2 size={16} className="shrink-0 text-text-secondary" />
            <p className="text-sm text-text-secondary">
              원본 이미지는 처리 후 즉시 파기하거나 보관할 수 있습니다.
            </p>
          </div>
          <div className="flex items-center gap-[8px]">
            <ShieldCheck size={16} className="shrink-0 text-text-secondary" />
            <p className="text-sm text-text-secondary">
              낮은 신뢰도 항목은 수동 보정 화면에서 직접 확인·수정할 수 있습니다.
            </p>
          </div>
        </div>

        {/* 직접 입력 링크 */}
        <button className="mt-[24px] text-sm font-bold text-info">
          OCR 없이 직접 입력하기 &rarr;
        </button>
      </main>
    </div>
  );
}
