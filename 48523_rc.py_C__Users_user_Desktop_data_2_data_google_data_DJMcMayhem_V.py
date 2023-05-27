n_maps = [
"nnoremap {} :norm ".format(chr(238)),
"nnoremap {} :%norm ".format(chr(206))
]

def source(V):
    for mapping in n_maps:
        V.nvim_instance.command(mapping)
