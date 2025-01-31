-- 外层循环控制行数
for i = 1, 9 do
    -- 内层循环控制列数
    for j = 1, i do
        -- 打印乘法表项，使用 string.format 格式化输出
        io.write(string.format("%d*%d=%-2d ", j, i, i * j))
    end
    -- 换行
    print()
end