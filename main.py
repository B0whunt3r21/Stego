from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    Label,
    Static,
    SelectionList,
    DirectoryTree,
    Switch,
)
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Static
from textual.reactive import reactive
from textual import on
from PIL import Image
from rich.text import Text



def imageToAscii(path, width=32):
    img = Image.open(path).convert("RGB")

    w, h = img.size
    aspect = h / w
    new_height = int(width * aspect * 0.5)
    img = img.resize((width, new_height))

    pixels = img.load()

    lines = []
    for y in range(0, new_height, 2):
        line = ""
        for x in range(width):
            top = pixels[x, y]
            bottom = pixels[x, y+1] if y+1 < new_height else top

            line += (
                f"\x1b[38;2;{top[0]};{top[1]};{top[2]}m"
                f"\x1b[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m▀"
            )

        line += "\x1b[0m"
        lines.append(line)

    return "\n".join(lines)



class IMG(Static):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def on_mount(self):
        ansiIMG = imageToAscii(self.path, width=32)
        ansi_text = Text.from_ansi(ansiIMG, no_wrap=True)
        self.update(ansi_text)



class FileSelect(Static):

    def compose(self) -> ComposeResult:
        yield Label("Image Select")
        yield DirectoryTree(".")



class StegoApp(App):
    CSS_PATH = "stego.css"

    BINDINGS = [
        ("d", "decode", "Decode")
        ,("e", "encode", "Encode")
        ,("i", "selectImage", "Select Image")
        ,("o", "outputFile", "Output-File")
        ,("p", "pwd", "Password")
        ,("q", "quit", "Quit")
        #,("^d", "toggleDark", "Toggle Dark")
    ]

    def action_toggle_dark(self):
        self.dark = not self.dark



    modeToggle = reactive(0)



    @on(Button.Pressed, "#btn_run")
    def execute(self):
        
        pass



    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(id="body"):

            with Horizontal(id="header"):
                yield IMG("encrypted.png", id="logo")
                yield Static("Stego", id="title")

            #In-File and e/d tgl
            with Horizontal(id="tgl_row"):
                with Horizontal(id="imSel"):
                    yield Label("Select Image:", id="lbl_img")
                    yield Button("Browse Image", id="btn_img")

                with Horizontal(id="tgl"):
                    yield Static("Encode", id="lbl_encode")
                    yield Switch(value=False, id="btn_toggle")
                    yield Static("Decode", id="lbl_decode")

            #Out-File
            with Horizontal(id="out_row"):
                yield Label("Output File-Name:", id="lbl_out")
                yield Input(placeholder="encrypted.png", id="out_name")

            #PWD and Run
            with Horizontal(id="pwd_row"):
                with Horizontal(id="pwd"):
                    yield Label("Password:", id="lbl_pwd")
                    yield Input(password=True, placeholder="••••••", id="pwd_in")

                with Horizontal(id="btn"):
                    yield Button("Run", id="btn_run")

        yield Footer()



    # --- ACTIONS ---
    def action_encode(self):
        self.query_one("#encode").label = "Encode"

    def action_decode(self):
        self.query_one("#decode").label = "Decode"

    def action_select_image(self):
        self.push_screen(FileSelect())


if __name__ == "__main__":
    app = StegoApp()
    app.run()

