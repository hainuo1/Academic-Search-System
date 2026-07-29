-- ============================================================
-- 引用关系模拟数据生成脚本
-- 气象科学研究数据平台 v6.1
-- 为数据库中已有的文献随机生成引用关系
-- 执行方式：psql -U postgres -d AcademicSearchDB -f gen_citations.sql
-- ============================================================

-- 假设当前数据库中 documents 表已有 N 篇文献（document_id 从 1 开始连续）
-- 每个文献随机引用 0~5 篇其他文献

DO $$
DECLARE
    doc RECORD;
    target_id INT;
    num_refs INT;
    selected_ids INT[] := '{}';
    candidate_id INT;
    max_id INT;
BEGIN
    SELECT MAX(document_id) INTO max_id FROM documents;
    RAISE NOTICE '文献总数: %', max_id;

    -- 遍历每一篇文献
    FOR doc IN SELECT document_id FROM documents ORDER BY document_id LOOP
        -- 随机决定引用 0~5 篇文献
        num_refs := floor(random() * 6)::INT;
        selected_ids := '{}';

        FOR i IN 1..num_refs LOOP
            -- 随机选一篇不同的文献（不能是自己，不能重复）
            FOR attempt IN 1..50 LOOP
                candidate_id := floor(random() * max_id)::INT + 1;
                IF candidate_id != doc.document_id
                   AND NOT (candidate_id = ANY(selected_ids)) THEN
                    selected_ids := array_append(selected_ids, candidate_id);
                    EXIT;
                END IF;
            END LOOP;
        END LOOP;

        -- 插入引用关系
        FOREACH target_id IN ARRAY selected_ids LOOP
            BEGIN
                INSERT INTO citation (source_document_id, target_document_id)
                VALUES (doc.document_id, target_id)
                ON CONFLICT DO NOTHING;
            EXCEPTION WHEN OTHERS THEN
                -- 跳过重复或非法引用
                NULL;
            END;
        END LOOP;
    END LOOP;

    RAISE NOTICE '引用关系生成完成！';
END $$;

-- 查看生成的引用数量
SELECT '引用关系总数' AS 统计项, COUNT(*) AS 数量 FROM citation
UNION ALL
SELECT '有引用的文献数', COUNT(DISTINCT source_document_id) FROM citation
UNION ALL
SELECT '被引用的文献数', COUNT(DISTINCT target_document_id) FROM citation;
