def analyze_results(rows):
    if not rows:
        return (
            "📊 <b>الإحصائيات</b>\n\n"
            "لا توجد نتائج كافية للتحليل."
        )

    values = [float(row[0]) for row in rows]
    total = len(values)

    average = sum(values) / total
    highest = max(values)
    lowest = min(values)

    under_2 = sum(1 for x in values if x < 2)
    from_2_to_5 = sum(1 for x in values if 2 <= x < 5)
    from_5_to_10 = sum(1 for x in values if 5 <= x < 10)
    over_10 = sum(1 for x in values if x >= 10)

    def pct(count):
        return count / total * 100

    return (
        "📊 <b>تحليل النتائج السابقة</b>\n\n"
        f"🔢 عدد النتائج: <b>{total}</b>\n"
        f"📈 المتوسط: <b>{average:.2f}x</b>\n"
        f"⬆️ أعلى نتيجة: <b>{highest:.2f}x</b>\n"
        f"⬇️ أقل نتيجة: <b>{lowest:.2f}x</b>\n\n"
        "📌 <b>التوزيع:</b>\n"
        f"• أقل من 2x: <b>{under_2}</b> ({pct(under_2):.1f}%)\n"
        f"• من 2x إلى أقل من 5x: <b>{from_2_to_5}</b> ({pct(from_2_to_5):.1f}%)\n"
        f"• من 5x إلى أقل من 10x: <b>{from_5_to_10}</b> ({pct(from_5_to_10):.1f}%)\n"
        f"• 10x أو أكثر: <b>{over_10}</b> ({pct(over_10):.1f}%)\n\n"
        "⚠️ هذه إحصائيات وصفية للنتائج السابقة فقط، "
        "وليست توقعاً للنتيجة القادمة."
    )
