from termighty import TextBox, Term, Listener
from termighty_input_box import InputBox

term = Term()
title_bar_height = 1

input_title = TextBox(-3, 0, -2, -1, background="Charcoal")
input_window = InputBox(-2, 0, -1, -1, line_numbers=False, background="Black")
output_title = TextBox(0, 0, 1, -1, background="Charcoal")
output_title.alignment = "center"
input_title.alignment = "center"
output_window = TextBox(1, 0, -3, -1, background="Black")

output_title(["Conversation History"])
output_window([""])
input_window([""])
input_title(["User Input"])

term.clear(flush=True)
Listener.start()
input_window.start()
input_title.start()
output_title.start()
output_window.start()
