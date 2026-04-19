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



class DirTree(DirectoryTree):
    def __init__(self, path, selector=None, **kwargs):
        super().__init__(path, **kwargs)
        self.__selector = selector

    @property
    def selector(self):
        return self.__selector
    
    @selector.setter
    def selector(self, selector):
        self.__selector = selector


    def filter_paths(self, paths):
        filtered = [
            path for path in paths
            if not path.name.startswith(".")
            ]
        
        if not self.selector:
            return filtered
        else:
            return [
                p for p in filtered
                if p.is_dir() or p.suffix.lower() == self.selector.lower()
            ]
    



class FileSelect(Static):
    def __init__(self, path, title, filter=None, **kwargs):
        super().__init__(**kwargs)
        self.__path = Path(path).resolve()
        self.__title = title
        self.__selected_file: Path | None = None
        self.__filter = filter
        self.__replacing = False


    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path):
        self.__path = Path(path).resolve()
    
    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def selected_file(self):
        return self.__selected_file
    
    @selected_file.setter
    def selected_file(self, selected_file):
        self.__selected_file = selected_file

    @property
    def filter(self):
        return self.__filter
    
    @filter.setter
    def filter(self, filter):
        self.__filter = filter


    BINDINGS = [
        ("backspace", "go_up", "Go Up")
        ,("u", "rootPath", "User Root")
        ,("p", "projPath", "Project Root")
    ]

    
    def action_rootPath(self):
        root = Path.home()
        if not root.exists():
            root = Path('./in/').resolve()
        self.replaceTree(root)


    def action_projPath(self):
        root = Path('.').resolve()
        self.replaceTree(root)

    
    def action_go_up(self):
        tree = self.query_one("#tree", DirectoryTree)
        current = tree.path
        parent = current.parent

        if parent == current:
            return

        self.replaceTree(parent)


    def replaceTree(self, new_path: Path):
        if self.__replacing:
            pass

        self._replacing = True

        old = self.query_one("#tree", DirectoryTree)
        parent = old.parent
        old.remove()

        def mount_new():
            new = DirTree(new_path, self.filter, id="tree")
            parent.mount(new)
            self.path = new_path
            self.update_breadcrumb(new_path)
            self.refresh(layout=True)

            self.__replacing = False

        self.call_after_refresh(mount_new)


    def update_breadcrumb(self, path: Path):
        self.query_one("#breadcrumb", Label).update(path.as_posix())


    def compose(self) -> ComposeResult:
        with Vertical(id="fileSelect"):
            yield Label(self.title, id="lbl_img")

            with Horizontal(id='toolbar'):
                yield Button("↑", id="btn_up")
                yield Label(self.path.as_posix(), id="breadcrumb")

            yield DirTree(self.path, self.filter, id="tree")


    @on(DirectoryTree.NodeExpanded)
    def update_on_dir_enter(self, event: DirectoryTree.NodeExpanded):
        self.path = event.node.path
        self.update_breadcrumb(self.path)

    @on(DirectoryTree.FileSelected)
    def file_selected(self, event: DirectoryTree.FileSelected):
        self.selected_file = event.path

    @on(DirectoryTree.NodeExpanded)
    @on(DirectoryTree.NodeCollapsed)
    def resize_tree(self):
        self.refresh(layout=True)

    @on(Button.Pressed, "#btn_up")
    def up_pressed(self):
        self.action_go_up()


    @property
    def value(self):
        return self.selected_file





class StegoApp(App):
    CSS_PATH = "stego.css"
    
    #Decode 0 / Encode 1
    mode = reactive(0)


    # --- ACTIONS ---
    BINDINGS = [
        ("d", "decode", "Decode")
        ,("e", "encode", "Encode")
        ,("r", "reload", "Reload")
        ,("q", "quit", "Quit")
        #,("^d", "toggleDark", "Toggle Dark")
    ]


    def action_reload(self):
        imgSel = self.query_one('#img_select', FileSelect)
        txtSel = self.query_one('#text_select', FileSelect)

        imgSel.replaceTree(imgSel.path)
        txtSel.replaceTree(txtSel.path)

        nameBox = self.query_one("#out_name", Input)
        pwdBox = self.query_one("#pwd_in", Input)
        nameBox.value = ''
        pwdBox.value = ''
        


    def action_toggleDark(self):
        self.dark = not self.dark


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
            outName = self.query_one('#out_name', Input)
            outName.placeholder = 'encoded.png'
        else:           # decode
            fileSel.display = False
            outName = self.query_one('#out_name', Input)
            outName.placeholder = 'message.txt'

  
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
            
            if outName.endswith('.png'):
                pass
            else:
                outName = outName + '.png'

            if text is None:
                self.notify("Please select a text file to encode.")

        self.action_reload()

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
                yield Static(id='spacer_tgl')

                with Horizontal(id="tgl"):
                    yield Static("Encode", id="lbl_encode")
                    yield Switch(value=False, id="btn_toggle")
                    yield Static("Decode", id="lbl_decode")
                              
                #Row 3

                #In-File
                yield FileSelect("./in/", 'Select image', '.png', id="img_select")
                
                #Row 4

                #File Select
                yield FileSelect("./in/", 'Select file to embed', id="text_select")
                
                #Row 5

                #Out-File and PWD
                with Horizontal(id="out_file"):
                    yield Label("Output File-Name:", id="lbl_out")
                    yield Input(placeholder="encoded.png", id="out_name")

                with Horizontal(id="pwd"):
                    yield Label("Password:", id="lbl_pwd")
                    yield Input(password=True, placeholder="••••••", id="pwd_in")
                                
                #Row 6

                #PWD and Run
                yield Static(id='spacer_out')

                with Horizontal(id="btn"):
                    yield Button("Run", id="btn_run")


        yield Footer()



if __name__ == "__main__":
    app = StegoApp()
    app.run()

