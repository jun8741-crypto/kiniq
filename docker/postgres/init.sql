-- asyncpg가 DB 미지정 시 username(ckduser)을 기본 DB로 사용하므로
-- 테스트 실행 시 maintenance DB로 필요함
CREATE DATABASE ckduser OWNER ckduser;

-- 애플리케이션 메인 DB (POSTGRES_DB 환경변수로도 생성되지만 명시적으로 선언)
-- 컨테이너 재생성 시에도 항상 존재하도록 보장
CREATE DATABASE ckd_challenge OWNER ckduser;
