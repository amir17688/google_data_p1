def get_embedded_nvim_args(platform, secondary_file_path):
    if platform == "Windows":
        #args = ["C:\\Neovim\\bin\\nvim.exe", "-i", "NONE", "-d", "NONE"]
        args = ["nvim.exe", "-i", "NONE", "-d", "NONE"]
    elif platform == "Linux":
        args = ["/usr/bin/nvim", "-i", "NONE", "-d", "NONE"]

    if secondary_file_path:
        args += [secondary_file_path]

    args += ["--embed"]

    return args

def get_socket_path(platform):
    if platform == "Windows":
        return "\\\\.\\pipe\\nvim"
    elif platform == "Linux":
        return "/tmp/nvim"

def get_external_nvim_command(platform, secondary_file_path):
    if platform == "Windows":
        #command = "START C:\\users\\jmhjr\\Desktop\\nvim-qt\\nvim-qt.exe \i NONE \d NONE {}"
        command = "START nvim-qt.exe \i NONE \d NONE {}"
    elif platform == "Linux":
        #command = "$TERM -e '/usr/bin/nvim -i NONE -d NONE {}'"
        command = "$TERM -e 'nvim -i NONE -d NONE {}'"

    return command.format(secondary_file_path)
