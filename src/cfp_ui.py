import flet as ft

def get_cfp_view(page: ft.Page, conf_info, on_back_click):
    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW, icon_size=18, icon_color="blue700", on_click=on_back_click),
                ft.Text("Call for Papers", size=16, weight="w600", color="blue700")
            ], spacing=10),
            ft.Row([
                ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED, size=20, color="grey600"),
                ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, size=15), radius=12, bgcolor="blue50"),
                ft.Text("Admin", size=13, weight="w500"),
            ], spacing=15)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.only(left=10, right=20, top=10, bottom=10),
        bgcolor="white",
        border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
    )

    # SIDEBAR (Timeline & AI)
    def timeline_step(date, label, is_deadline=False):
        return ft.Row([
            ft.Container(width=12, height=12, border_radius=6, border=ft.border.all(2, "grey500"), bgcolor="white"),
            ft.Text(date, size=12, weight="bold"),
            ft.Text(label, size=12, color="red" if is_deadline else "black")
        ], spacing=15)

    sidebar = ft.Container(
        width=350, padding=30, bgcolor="white", border_radius=20,
        border=ft.border.all(2, "#448AFF"),
        content=ft.Column([
            ft.Container(
                content=ft.Text("Status: Accepting Submissions", color="white", weight="bold", size=12),
                bgcolor="#64B5F6", padding=10, border_radius=ft.border_radius.only(top_left=15, top_right=15),
                alignment=ft.alignment.center, margin=ft.margin.only(top=-30, left=-30, right=-30)
            ),
            ft.Text("Important Dates", size=18, weight="bold"),
            ft.Stack([
                ft.Container(margin=ft.margin.only(left=5, top=10), width=2, height=80, bgcolor="grey300"),
                ft.Column([
                    timeline_step("Feb 01, 2026: ", "Submission Deadline", True),
                    timeline_step("Feb 05, 2026: ", "Notification Date"),
                    timeline_step("Feb 15, 2026: ", "Conference Date"),
                ], spacing=20)
            ]),
            ft.Container(
                padding=15, border=ft.border.all(1, "#BBDEFB"), border_radius=12,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.icons.SMART_TOY, size=20), ft.Text("AI Recommendation", weight="bold", size=13)]),
                    ft.Text(f"Based on your profile, your paper is a {conf_info['match']}% match.", size=11, color="grey700")
                ])
            ),
            ft.ElevatedButton(
                "Submit Your Paper", bgcolor="#007BFF", color="white", 
                width=300, height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20))
            )
        ], spacing=20)
    )

    # MAIN CONTENT
    main_body = ft.Container(
        expand=True, bgcolor="#E3F2FD", border_radius=15, padding=40,
        content=ft.Row([
            ft.Column([
                ft.Text("The 5th International Conference on Green Transportation", size=22, weight="w500"),
                ft.Text(conf_info["conf_name"], size=30, weight="bold", color="#007BFF"),
                ft.Text("Introduction", size=20, weight="bold"),
                ft.Text(f"Insights on {conf_info['topic']}.", size=14),
                ft.Text("Conference Topics", size=20, weight="bold"),
                ft.Text("• Sustainable Logistics\n• AI in Traffic Management", size=14, line_height=1.5),
                ft.Text("Submission Guidelines", size=20, weight="bold"),
                ft.Text("• System only accepts .PDF format\n• Use AI-assisted tools for checks.", size=14),
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            sidebar
        ], vertical_alignment=ft.CrossAxisAlignment.START)
    )

    return ft.Column([header, ft.Container(main_body, padding=20, expand=True)], expand=True, spacing=0)