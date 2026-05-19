-- asyncpg가 DB 미지정 시 username(ckduser)을 기본 DB로 사용하므로
-- 테스트 실행 시 maintenance DB로 필요함
CREATE DATABASE ckduser OWNER ckduser;
