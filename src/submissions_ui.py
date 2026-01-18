import flet as ft

def main(page: ft.Page):
    page.title = "UTH-ConfMS - Submissions"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8F9FA"
    page.window_width = 1200
    page.window_height = 850
    page.padding = 0
    # 1. Sidebar va Header
    def create_header(title):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.MENU, color="black"),
                ft.Text(title, size=20, weight="bold"),
                ft.Row([
                    ft.Icon(ft.icons.DARK_MODE_OUTLINED),
                    ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED),
                    ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON)),
                    ft.Text("Admin", weight="bold")
                ], spacing=15)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10, bgcolor="white"
        )

    # 2. SUBMISSIONS LIST
    def submissions_view():
        notes = ft.Container(
            content=ft.Column([
                ft.Text("Important Notes", weight="bold", size=16),
                ft.Text("System only accepts .PDF format\nAll edits or withdrawals must be completed before the deadline"),
            ]),
            padding=20, border=ft.border.all(1, "blue200"), border_radius=10, expand=2
        )

        # AI card
        ai_stats = ft.Row([
            ft.Container(content=ft.Column([ft.Text("AI Success Rate"), ft.Text("85%", size=25, weight="bold")], horizontal_alignment="center"), border=ft.border.all(1, "blue200"), padding=15, border_radius=10, expand=1),
            ft.Container(content=ft.Column([ft.Text("Suggestions Applied"), ft.Text("24", size=25, weight="bold")], horizontal_alignment="center"), border=ft.border.all(1, "blue200"), padding=15, border_radius=10, expand=1),
            ft.Container(content=ft.Column([ft.Text("Grammar Errors Fixed"), ft.Text("12", size=25, weight="bold")], horizontal_alignment="center"), border=ft.border.all(1, "blue200"), padding=15, border_radius=10, expand=1),
        ], spacing=15, expand=3)

        # Bảng dữ liệu
        table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Track/Topic")),
                ft.DataColumn(ft.Text("Title")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("#001")),
                    ft.DataCell(ft.Text("AI")),
                    ft.DataCell(ft.Text("Article 1")),
                    ft.DataCell(ft.Text("Submitted", color="blue")),
                    ft.DataCell(ft.Text("Camera-ready")),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("#002")),
                    ft.DataCell(ft.Text("Logistics")),
                    ft.DataCell(ft.Text("Article 2")),
                    ft.DataCell(ft.Text("Accept", color="green")),
                    ft.DataCell(ft.Text("Under review")),
                ]),
            ]
        )

        return ft.Column([
            create_header("Submissions"),
            ft.Padding(padding=20, content=ft.Column([
                ft.Text("My Submissions", size=18, weight="bold"),
                ft.Row([notes, ai_stats], spacing=20),
                ft.Row([
                    ft.Text("Recent submissions", weight="bold"),
                    ft.ElevatedButton("Create New Submission", icon=ft.icons.ADD, bgcolor="blue", color="white", on_click=lambda _: show_create_view())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                table
            ], spacing=20))
        ], scroll=ft.ScrollMode.AUTO)

    # 3. CREATE SUBMISSION
    def create_new_view():
        form_content = ft.Column([
            ft.TextField(label="Title *", border_radius=5),
            ft.Dropdown(label="Track/Topic *", options=[ft.dropdown.Option("Information Technology"), ft.dropdown.Option("AI")], border_radius=5),
            ft.TextField(label="Please fill in the content clearly...", multiline=True, min_lines=8, border_radius=5),
            ft.Container(
                content=ft.Text("Click or drag PDF file here\nSystem only accepts .PDF format", text_align="center", color="grey"),
                padding=30, border=ft.border.all(1, "grey400"), border_style=ft.BorderStyle.DASHED, border_radius=10, alignment=ft.alignment.center
            ),
            ft.TextField(label="Full Name:", border_radius=5),
            ft.Row([
                ft.ElevatedButton("Submit", bgcolor="blue", color="white", expand=True),
                ft.ElevatedButton("Reset", bgcolor="green", color="white", expand=True),
                ft.ElevatedButton("Cancel", bgcolor="red", color="white", expand=True, on_click=lambda _: show_list_view()),
            ], spacing=10)
        ], spacing=15, expand=2)

        ai_sidebar = ft.Container(
            content=ft.Column([
                ft.Text("AI Suggestions", weight="bold"),
                ft.Row([ft.Chip(label="Information Technology"), ft.Chip(label="Logistics")], wrap=True),
                ft.Row([ft.Chip(label="Artificial Intelligence"), ft.Chip(label="Optimization")], wrap=True),
            ], spacing=10),
            expand=1, padding=20, bgcolor="white", border=ft.border.all(1, "grey200"), border_radius=10
        )

        return ft.Column([
            create_header("Create New Submission"),
            ft.Padding(padding=20, content=ft.Column([
                ft.Text("Submit New Paper", size=18, weight="bold"),
                ft.Row([form_content, ai_sidebar], vertical_alignment="start", spacing=30)
            ]))
        ], scroll=ft.ScrollMode.AUTO)

    # --- LOGIC CHUYỂN TRANG ---
    def show_list_view():
        page.clean()
        page.add(submissions_view())
    
    def show_create_view():
        page.clean()
        page.add(create_new_view())

    show_list_view()

ft.app(target=main)