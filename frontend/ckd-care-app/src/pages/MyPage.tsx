import { Heart, Bell, Lock, Headphones } from "lucide-react";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { Tag } from "../components/Tag";
import { ListItem } from "../components/ListItem";
import { TextInput } from "../components/TextInput";

export function MyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="04 · 마이페이지 (REQ-USR-01)" />
      <TopNav />
      <main className="flex flex-1 items-start justify-center gap-[32px] p-[32px]">
        {/* 왼쪽: 프로필 + 메뉴 */}
        <div className="flex w-[360px] flex-col gap-[16px]">
          {/* 프로필 카드 */}
          <div className="flex flex-col items-center gap-[12px] rounded-md border border-border bg-bg p-[24px]">
            {/* 아바타 */}
            <div className="flex h-[80px] w-[80px] items-center justify-center rounded-full bg-bg-alt">
              <span className="text-2xl text-text-muted">H</span>
            </div>
            <p className="text-lg font-bold text-text-primary">홍길동</p>
            <p className="text-sm text-text-secondary">user@example.com</p>
            <Tag label="G2 · 경계군" />
          </div>

          {/* 메뉴 리스트 */}
          <div className="flex flex-col gap-[8px]">
            <ListItem
              icon={Heart}
              title="내 건강 데이터"
              subtitle="건강검진 결과 및 추이 확인"
            />
            <ListItem
              icon={Bell}
              title="알림 설정"
              subtitle="푸시 알림 및 리마인더 관리"
            />
            <ListItem
              icon={Lock}
              title="비밀번호 변경"
              subtitle="계정 보안 설정"
            />
            <ListItem
              icon={Headphones}
              title="고객센터"
              subtitle="문의 및 FAQ"
            />
          </div>
        </div>

        {/* 오른쪽: 회원 탈퇴 */}
        <div className="flex w-[480px] flex-col gap-[16px] rounded-md border border-danger bg-bg p-[24px]">
          <h2 className="text-lg font-bold text-danger">회원 탈퇴</h2>
          <p className="text-sm text-text-secondary">
            탈퇴 시 모든 건강 데이터와 챌린지 기록이 영구 삭제되며 복구할 수
            없습니다. 신중하게 결정해주세요.
          </p>
          <TextInput
            label="비밀번호 확인"
            placeholder="현재 비밀번호를 입력하세요"
          />
          <button className="flex h-[44px] items-center justify-center rounded-md bg-danger px-[16px] py-[12px] text-sm font-bold text-bg">
            회원 탈퇴
          </button>
        </div>
      </main>
    </div>
  );
}
