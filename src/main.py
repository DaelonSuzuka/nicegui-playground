from nicegui import ui
from bs4 import BeautifulSoup as bs


default_code = """with ui.row():
    ui.button('one')
    ui.button('two')
"""

ui.add_head_html(
    """<script defer data-domain="playground.daelon.net" src="https://plausible.daelon.net/js/script.js"></script>""",
    shared=True,
)


class PlaygroundPage:
    def __init__(self) -> None:
        with ui.row(wrap=False).classes('h-1/2 w-full'):
            with ui.column().classes('h-full w-1/2'):
                with ui.row().classes('w-full justify-between'):
                    ui.label('Write NiceGUI code here:')
                    with ui.row():
                        ui.button('clear', on_click=self.clear)
                        ui.button('run', on_click=self.run)
                self.code = ui.codemirror(
                    default_code, language='Python', theme='vscodeDark'
                ).classes('w-full no-shadow')

            with ui.column().classes('h-full w-1/2'):
                ui.label('Generated UI:')
                ui.label()
                ui.label()
                self.output = ui.card().classes('h-full w-full no-shadow border-[1px]')
        ui.label('Generated HTML:')
        self.html = ui.code(language='html').classes('w-full no-shadow')

    def clear(self):
        self.output.clear()
        self.html.clear()

    async def run(self):
        new_code = self.code.value

        self.output.clear()
        try:
            with self.output:
                exec(new_code)

            js = f'new XMLSerializer().serializeToString(document.getElementById("c{self.output.id}"))'
            result = await ui.run_javascript(js)

            prettyHTML = bs(result).prettify()
            self.html.set_content(prettyHTML)
        except Exception as e:
            ui.notify(e)


@ui.page('/')
async def index():
    page = PlaygroundPage()

    await page.run()


ui.run(
    title='NiceGUI Playground',
    dark=True,
)
