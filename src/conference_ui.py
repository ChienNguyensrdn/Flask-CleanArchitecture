import flet as ft
from cfp_ui import get_cfp_view

def main(page: ft.Page):
    page.title = "UTH-ConfMS - Conference"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "white" 
    page.window_width = 1300
    page.window_height = 900
    page.padding = 0

    # 1. DỮ LIỆU MẪU
    conference_data = [
        {"conf_name": "ICGT 2026", "paper_title": "The 5th International Conference on Green Transportation", "topic": "Sustainable Logistics, Electric Vehicles, Green Maritime.", "match": 98},
        {"conf_name": "AI-CO 2026", "paper_title": "Ứng dụng AI trong phân loại hàng hóa", "topic": "Artificial Intelligence, Deep Learning, Optimization.", "match": 95},
        {"conf_name": "LogiTech 2026", "paper_title": "Tối ưu hóa chuỗi cung ứng bằng IoT", "topic": "Supply Chain, Internet of Things, Smart Warehousing.", "match": 88},
        {"conf_name": "ICGT 2026", "paper_title": "The 5th International Conference on Green Transportation", "topic": "Sustainable Logistics...", "match": 98},
        {"conf_name": "AI-CO 2026", "paper_title": "Ứng dụng AI trong phân loại...", "topic": "Artificial Intelligence...", "match": 92},
        {"conf_name": "LogiTech 2026", "paper_title": "Tối ưu hóa chuỗi cung ứng...", "topic": "Supply Chain...", "match": 85},
    ]

    def go_back(e):
        show_conference_page()

    def go_to_cfp(e, item):
        page.controls.clear()
        page.add(get_cfp_view(page, item, go_back))
        page.update()

    # 2. COMPONENT: HEADER
    def create_header():
        return ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.MENU, icon_color="grey700"),
                ft.Row([
                    ft.Icon(ft.icons.NIGHTLIGHT_ROUND, size=20, color="grey800"),
                    ft.Stack([
                        ft.Icon(ft.icons.NOTIFICATIONS, size=20, color="grey800"),
                        ft.Container(bgcolor="red", width=10, height=10, border_radius=5, 
                                     content=ft.Text("3", size=7, color="white", text_align="center"),
                                     margin=ft.margin.only(left=12, top=-2))
                    ]),
                    ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, size=15), radius=12, bgcolor="blue700"),
                    ft.Text("Admin", size=13, weight="w500"),
                    ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN, size=18)
                ], spacing=15)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(left=10, right=20, top=5, bottom=5),
            bgcolor="white",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
        )

    # 3. COMPONENT: Conference car
    def create_conference_card(item):
        return ft.Container(
            width=350,
            padding=25,
            bgcolor="white",
            border_radius=20,
            border=ft.border.all(1, "#E3F2FD"),
            content=ft.Column([
                ft.Row([
                    ft.Text(item["conf_name"], size=22, weight="bold", color="#007BFF"),
                    ft.Container(
                        content=ft.Text(f"AI Match: {item['match']}%", size=9, color="#2E7D32", weight="bold"),
                        bgcolor="#E8F5E9", padding=ft.padding.symmetric(horizontal=10, vertical=5), border_radius=15
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Text(item["paper_title"], size=13, weight="w500", color="black"),
                ft.Text(f"Topic: {item['topic']}", size=11, color="grey700"),
                
                ft.Container(height=10), 

                ft.Row([
                    ft.OutlinedButton(
                        "View Details", 
                        style=ft.ButtonStyle(color="#007BFF", side={"": ft.BorderSide(1, "#007BFF")}),
                        on_click=lambda e: go_to_cfp(e, item),
                        height=35
                    ),
                    ft.ElevatedButton(
                        "Submit Now", 
                        bgcolor="#007BFF", color="white",
                        on_click=lambda e: go_to_cfp(e, item),
                        height=35
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=8)
        )

    def show_conference_page():
        page.controls.clear()
        search_filter_bar = ft.Row([
            ft.TextField(
                hint_text="Search conference name, acronym...",
                prefix_icon=ft.icons.SEARCH,
                expand=True,
                border_radius=25,
                bgcolor="white",
                height=45,
                text_size=13,
                border_color="#DDDDDD"
            ),
            ft.Dropdown(label="Topic", options=[ft.dropdown.Option("All")], width=120, height=45, bgcolor="#E3F2FD", border_radius=10, text_size=12),
            ft.Dropdown(label="Status", options=[ft.dropdown.Option("All")], width=120, height=45, bgcolor="#E3F2FD", border_radius=10, text_size=12),
            ft.Dropdown(label="Location", options=[ft.dropdown.Option("All")], width=120, height=45, bgcolor="#E3F2FD", border_radius=10, text_size=12),
        ], spacing=15)

        grid = ft.GridView(
            runs_count=3,
            max_extent=400,
            spacing=30,
            run_spacing=30,
            controls=[create_conference_card(item) for item in conference_data],
            expand=True
        )

        page.add(
            ft.Column([
                create_header(),
                ft.Container(
                    padding=30,
                    expand=True,
                    content=ft.Column([
                        ft.Text("Available Conference", size=18, weight="bold"),
                        search_filter_bar,
                        ft.Container(
                            content=grid,
                            bgcolor="#F1F8FF", 
                            padding=40,
                            border_radius=20,
                            expand=True
                        ),
                        # Phân trang
                        ft.Row([
                            ft.TextButton("< Previous", style=ft.ButtonStyle(color="grey600")),
                            ft.Text("1   2   3   4   ...   13   14", size=12),
                            ft.TextButton("Next >", style=ft.ButtonStyle(color="grey600")),
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=15)
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_conference_page()

ft.app(target=main)