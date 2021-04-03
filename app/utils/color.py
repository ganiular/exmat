def print_color(text,r=0,g=0,b=0):
    if not (r or g or b):
        print(f"\033[7m {text} \033[0m")
    else:
        print(f"\033[38;2;{r};{g};{b}m {text} \033[0m")

def color_text(text,r=0,g=0,b=0):
    if not (r or g or b):
        return (f"\033[7m {text} \033[0m")
    else:
        return (f"\033[38;2;{r};{g};{b}m {text} \033[0m")
