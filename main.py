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
from textual.containers import Container, Horizontal, Vertical, VerticalScroll, Grid
from textual.widgets import Static
from textual.reactive import reactive
from textual import on
from PIL import Image
from rich.text import Text

from platformdirs import PlatformDirs
from pathlib import Path

from Steganography import Steganography



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
    def __init__(self, path, title, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.title = title
        self.selected_path: Path | None = None


    def compose(self) -> ComposeResult:
        yield Label(self.title, id="lbl_img")
        yield DirectoryTree(self.path, id="tree")


    @on(DirectoryTree.FileSelected)
    def file_selected(self, event: DirectoryTree.FileSelected):
        self.selected_path = event.path
        

    @on(DirectoryTree.NodeExpanded)
    @on(DirectoryTree.NodeCollapsed)
    def resize_tree(self):
        self.refresh(layout=True)


    @property
    def value(self):
        return self.selected_path



class StegoApp(App):
    CSS_PATH = "stego.css"
    
    #Decode 0 / Encode 1
    mode = reactive(0)

    imgPath = reactive(None)
    filePathh = reactive(None)


    def replaceImgTree(self, path):
        parent = self.query_one("#imgSel", Vertical)
        old = parent.query_one("#img_select", FileSelect)

        old.remove()

        def mount_new():
            new = FileSelect(path,'Select image', id="img_select")
            parent.mount(new)
            parent.refresh(layout=True)

        self.call_after_refresh(mount_new)


    def replaceTxtTree(self, path):
        parent = self.query_one("#txtSel", Vertical)
        old = parent.query_one("#text_select", FileSelect)

        old.remove()

        def mount_new():
            new = FileSelect(path, 'Select file to embed', id="text_select")
            parent.mount(new)
            parent.refresh(layout=True)

        self.call_after_refresh(mount_new)
    


    # --- ACTIONS ---
    BINDINGS = [
        ("d", "decode", "Decode")
        ,("e", "encode", "Encode")
        #,("i", "imgRootPath", "Images")
        #,("I", "imgProjPath", "Project Root")
        #,("t", "txtRootPath", "Images")
        #,("T", "txtProjPath", "Project Root")
        ,("r", "reload", "Reload")
        ,("q", "quit", "Quit")
        #,("^d", "toggleDark", "Toggle Dark")
    ]

    def action_reload(self):
        self.replaceImgTree("./in/")
        self.replaceTxtTree("./in/")


    def action_toggleDark(self):
        self.dark = not self.dark

    '''
    def action_imgRootPath(self):
        root = Path(PlatformDirs().user_pictures_dir)
        if not root.exists():
            root = Path.home()
        self.replaceImgTree(root)

    def action_imgProjPath(self):
        root = './in/'
        self.replaceImgTree(root)


    def action_txtRootPath(self):
        root = Path(PlatformDirs().user_documents_dir)
        if not root.exists():
            root = Path.home()
        self.replaceTxtTree(root)

    def action_txtProjPath(self):
        root = './in/'
        self.replaceTxtTree(root)
    '''

    def action_decode(self):
        self.mode = 1
        toggle = self.query_one("#btn_toggle", Switch) #Sub rows to single classes for action handling?
        toggle.value = True


    def action_encode(self):
        self.mode = 0
        toggle = self.query_one("#btn_toggle", Switch) #Sub rows to single classes for action handling?
        toggle.value = False


    def action_select_image(self):
        self.push_screen(FileSelect())


    def watch_mode(self, mode: int):
        fileSel = self.query_one("#text_select", FileSelect)

        if mode == 0:   # encode
            fileSel.display = True
        else:           # decode
            fileSel.display = False

  
    @on(Switch.Changed, "#btn_toggle")
    def toggle_changed(self, event: Switch.Changed):
        self.mode = event.value


    @on(Button.Pressed, "#btn_run")
    def execute(self):
        img = self.query_one("#img_select", FileSelect).value
        outName = self.query_one("#out_name", Input).value
        pwd = self.query_one("#pwd_in", Input).value
        text = None

        if img is None:
            self.notify("Please select an image.")
            
        if self.mode == 0: #Encode
            text = self.query_one("#text_select", FileSelect).value
            if text is None:
                self.notify("Please select a text file to encode.")

        
        stego = Steganography(self.mode, outName, pwd, img, text)
        stego.run()



    #Layout
    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(id="scroll"):

            with VerticalScroll(id="body"):

                #Row 1

                #Favicon and Title
                with Horizontal(id="favicon"):
                    yield IMG("assets/Stego.png", id="logo")

                with Horizontal(id="header"):
                    yield Static("Stego", id="title")

                #Row 2

                #Mode Switch
                yield Static(id='tglSpacer')

                with Horizontal(id="tgl"):
                    yield Static("Encode", id="lbl_encode")
                    yield Switch(value=False, id="btn_toggle")
                    yield Static("Decode", id="lbl_decode")
                              
                #Row 3

                #In-File and e/d tgl
                with Vertical(id="imgSel"):
                    yield FileSelect("./in/", 'Select image', id="img_select")

                with Vertical(id="txtSel"):
                    yield FileSelect("./in/", 'Select file to embed', id="text_select")


                #Row 4

                #Out-File
                with Horizontal(id="out_file"):
                    yield Label("Output File-Name:", id="lbl_out")
                    yield Input(placeholder="encrypted.png", id="out_name")
                
                yield Static(id='outSpacer')
                
                #Row 5

                #PWD and Run
                with Horizontal(id="pwd"):
                    yield Label("Password:", id="lbl_pwd")
                    yield Input(password=True, placeholder="••••••", id="pwd_in")

                with Horizontal(id="btn"):
                    yield Button("Run", id="btn_run")


        yield Footer()



if __name__ == "__main__":
    app = StegoApp()
    app.run()

