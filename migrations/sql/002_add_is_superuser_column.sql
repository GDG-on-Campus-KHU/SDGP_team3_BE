-- 이미 컬럼이 존재하지 않는 경우에만 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'is_superuser'
    ) THEN
        ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;
    END IF;
END
$$;