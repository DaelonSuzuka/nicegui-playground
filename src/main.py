from nicegui import ui
from bs4 import BeautifulSoup as bs
import base64


default_code = """with ui.row():
    ui.button('one')
    with ui.button('two'):
        ui.badge('1', color='red').props('floating')
"""

ui.add_head_html(
    """<script defer data-domain="playground.daelon.net" src="https://plausible.daelon.net/js/script.js"></script>""",
    shared=True,
)
ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />', shared=True)


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
        new_code: str = self.code.value

        self.output.clear()
        try:
            with self.output:
                exec(new_code)  #! lmao

            js = f'new XMLSerializer().serializeToString(document.getElementById("c{self.output.id}"))'
            result = await ui.run_javascript(js, timeout=3.0)

            soup = bs(result, features="html.parser")

            for span in soup.find_all('span', 'q-focus-helper'):
                span.decompose()

            for span in soup.find_all('span', 'block'):
                span.unwrap()

            soup
            prettyHTML = soup.prettify()
            self.html.set_content(prettyHTML)

            data = base64.urlsafe_b64encode(new_code.encode()).decode()
            ui.run_javascript(f"""
                    var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?data={data}";
                    window.history.pushState({{path:newurl}}, '', newurl);
            """)
        except Exception as e:
            ui.notify(e)


@ui.page('/')
async def index(data: str = None):
    with ui.header().classes('justify-between'):
        ui.button('NiceGUI Playground', on_click=lambda: ui.navigate.to('/')).props('flat color=white size=125%')
        with ui.row():
            ui.button(icon='eva-github', on_click=lambda: ui.navigate.to('https://github.com/DaelonSuzuka/nicegui-playground')).props('flat color=white size=125%')

    page = PlaygroundPage()
    if data:
        try:
            code = base64.urlsafe_b64decode(data.encode()).decode()
            page.code.value = code
        except:
            pass

    await page.run()


ui.run(
    title='NiceGUI Playground',
    dark=True,
)
