from nicegui import ui
from bs4 import BeautifulSoup as bs


code = """with ui.row():
    ui.button('one')
    ui.button('two')
"""


class PlaygroundPage:
    def __init__(self) -> None:
        with ui.row(wrap=False).classes('h-1/2 w-full'):
            with ui.column().classes('h-full w-1/2'):
                with ui.row().classes('w-full'):
                    ui.button('run', on_click=self.run)
                self.code = ui.codemirror(
                    code, language='Python', theme='vscodeDark'
                ).classes('w-full')
            self.output = ui.card().classes('h-full w-1/2')

        self.html = ui.code(language='html').classes('w-full')

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
    PlaygroundPage()


ui.run(
    title='NiceGUI Playground',
    dark=True,
)
