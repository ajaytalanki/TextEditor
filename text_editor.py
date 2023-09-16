from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os

# points to the current file path that is being edited
global open_filename
open_filename = False

# text that is being selected
global highlighted_text
highlighted_text = False

# determines if there are changes made to the file that aren't saved
global unsaved_changes 
unsaved_changes = False

# the last saved text content of the file in the editor
global saved_content
saved_content = False

global find_entry
find_entry = None

window = Tk()
window.title("Text Editor")
window.iconbitmap("notepad.ico")
window.geometry("1200x660")

def create_new_file(signal=None):

    window.title("Untitled")

    # there is no open file yet
    global open_filename
    open_filename = False

    # delete the current text to start new file
    text_box.delete("1.0", END)

    # no saved content 
    global saved_content
    saved_content = False
    
def open_file(signal=None):

    # deletes the current contents of text editor
    text_box.delete("1.0", END)

    # grabs path of new file
    file_path = filedialog.askopenfilename(title="Open File")

    # user selected a file, so change the open file
    if file_path:
        global open_filename
        open_filename = file_path

    # strips the path from filename to rename window
    file_name = os.path.basename(file_path)
    window.title(file_name)

    # copies the contents of the open file into the text box
    file_path = open(file_path, 'r')
    contents = file_path.read()
    text_box.insert(END, contents)

    # sets the saved_content to the current text of the newly opened file
    global saved_content
    saved_content = text_box.get(1.0, END)

    file_path.close()

def save(signal=None):
    global open_filename

    # if there is an open file
    if open_filename:

        # updates the saved_content
        global saved_content
        saved_content = text_box.get(1.0, END)

        # there are no unsaved changes now
        global unsaved_changes
        unsaved_changes = False

        # save the contents of the editor to the actual file
        file = open(open_filename, 'w')
        file.write(text_box.get(1.0, END))
        file.close()

    # user tried to save text when there is no open file, so call save_as
    else:
        save_as()

def save_as(signal=None):
    saved_file_path = filedialog.asksaveasfilename(defaultextension="*.txt", filetypes=(("Text Files", "*.txt"), ("All files", "*.*")))
    if saved_file_path:

        # updates the open file
        global open_filename
        open_filename = saved_file_path

        # updates the saved_content
        global saved_content
        saved_content = text_box.get(1.0, END)

        # no unsaved changes
        global unsaved_changes
        unsaved_changes = False

        # rename the window
        saved_file_name = os.path.basename(saved_file_path)
        window.title(saved_file_name)

        # write the contents of the text box to the corresponding file
        saved_file_path = open(saved_file_path, 'w')
        saved_file_path.write(text_box.get("1.0", END))
        saved_file_path.close()

# deletes the current highlighted text and saves it into the clipboard
def cut(signal):
    global highlighted_text

    # user entered "Ctrl + X"
    if signal:
        highlighted_text = window.clipboard_get()

    # user clicked cut command
    else:
        if text_box.selection_get():

            # get highlighted text
            highlighted_text = text_box.selection_get()

            # deletes the current selection of text
            text_box.delete("sel.first", "sel.last")

            # add highlighted text to clipboard
            window.clipboard_clear()
            window.clipboard_append(highlighted_text)

# copies the current highlighted text to the clipboard
def copy(signal):
    global highlighted_text

    # user entered "Ctrl + C"
    if signal:
        highlighted_text = window.clipboard_get()

    if text_box.selection_get():

        # add highlighted text to clipboard
        highlighted_text = text_box.selection_get()
        window.clipboard_clear()
        window.clipboard_append(highlighted_text)

# inserts the highlighted text to the current position
def paste(signal):
    global highlighted_text

    # user entered bind
    if signal:
        highlighted_text = window.clipboard_get()

    # user clicked paste button 
    else:
        if highlighted_text:
            
            # get current position
            pos = text_box.index(INSERT)

            # insert copied text
            text_box.insert(pos, highlighted_text)

def show_find_entry(signal=None):

    # sets up the toplevel for the find_entry
    find_dialog = Toplevel(window)
    find_dialog.title("Find")
    find_label = Label(find_dialog, text="Find:")
    find_label.grid(row=0, column=0, padx=5, pady=5)
    find_dialog.geometry("200x30")

    # displays find_entry
    global find_entry
    find_entry = Entry(find_dialog)
    find_entry.delete(0, END)
    find_entry.grid(row=0, column=1, padx=5, pady=5)
    find_entry.focus_set()
    find_entry.bind("<Return>", find)  

def find(signal):

    # grabs the word to search for 
    global find_entry
    query = find_entry.get()

    # remove the tags from previous seraches
    text_box.tag_remove("found", "1.0", END)

    if query:

        # initializes start to the beginning of file
        start = "1.0"
        while True:

            # sets start to the beginning of word
            start = text_box.search(query, start, stopindex=END)

            # end of file
            if not start:
                break

            # sets the end position to the end of the word and sets tag
            end = f"{start}+{len(query)}c"
            text_box.tag_add("found", start, end)

            # sets the start position to the end of the word and repeat process
            start = end

        # highlight the found words with color
        text_box.tag_config("found", background="#FFFF99", foreground="#000080")

# clears the highlighted words after using the "Find" command
def clear_highlight():
    text_box.tag_remove("found", "1.0", END)
    
def replace_command(sginal=None):

    replace_dialog = Toplevel(window)
    replace_dialog.title("Replace")

    # creates the label and text entry for the word to replace
    replace_word_label = Label(replace_dialog, text="Replace word:")
    replace_word_label.grid(row=0, column=0, padx=5, pady=5)
    replace_word_entry = Entry(replace_dialog)
    replace_word_entry.grid(row=0, column=1, padx=5, pady=5)

    # creates the label and text entry for the replacement
    replace_with_label = Label(replace_dialog, text="Replace with:")
    replace_with_label.grid(row=1, column=0, padx=5, pady=5)
    replace_with_entry = Entry(replace_dialog)
    replace_with_entry.grid(row=1, column=1, padx=5, pady=5)

    def perform_replace(replace_word, replace_with):
        if replace_word:

            # finds the first occurance of the word to replace
            start = text_box.search(replace_word, "1.0", END)
            while start:

                # finds the end of the word
                end = f"{start}+{len(replace_word)}c"

                # replace word 
                text_box.delete(start, end)
                text_box.insert(start, replace_with)

                # search for next occurance
                start = text_box.search(replace_word, end, END)
        replace_dialog.destroy()

    # creates the button to perform replacement
    replace_button = Button(replace_dialog, text="Replace", command=lambda: perform_replace(replace_word_entry.get(), replace_with_entry.get()))
    replace_button.grid(row=2, columnspan=2, padx=5, pady=5)

# there are unsaved changes in the text editor file
def mark_unsaved(signal=None):
    global unsaved_changes
    unsaved_changes = True

def quit():

    global unsaved_changes
    global saved_content

    # gets the current content to compare with the previously saved content
    curr_content = text_box.get(1.0, END)

    # text_box was empty when user attempted to exit window
    if(curr_content == "" or curr_content == "\n"):
        curr_content = False

    # user opened new file and left editor empty
    if(not saved_content and not curr_content):
        window.destroy()

    # user attempted to quit with unsaved changes
    elif unsaved_changes and curr_content != saved_content:
        result = messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to save before quitting?")
        
        # user selected yes
        if result: 
            save()

        # user selected no
        window.destroy()

    # no unsaved changes, so quit the program without prompting the user
    else:
        window.destroy()

# sets the tab spaces to 2 instead of 8
def insert_tab(signal=None):
    text_box.insert(INSERT, "  ")
    return 'break'

# window frame for the program
frame = Frame(window)
frame.pack(pady=5)

# menu bar for the File and Edit menus
menu_bar = Menu(window)
window.config(menu=menu_bar)

# creates a vertical scroll bar on the right side of screen
scroll_bar = Scrollbar(frame)
scroll_bar.pack(side = RIGHT, fill=Y)

# creates the text_box which will be the contents of each file
text_box = Text(frame, width=130, height=50, font=("Consolas", 12), selectbackground="#0066CC", undo=True, yscrollcommand=scroll_bar.set)
text_box.pack()

# provides the vertical scrolling functionality for the text_box widget.
scroll_bar.configure(command=text_box.yview)

# initializes and populates the File menu commands
file_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New File", accelerator="Ctrl + n",  command = create_new_file)
file_menu.add_command(label="Open File", accelerator="Ctrl + o", command=open_file)
file_menu.add_command(label="Save File", accelerator="Ctrl + s", command=save)
file_menu.add_command(label="Save File As", accelerator="Ctrl + a", command=save_as)

# initializes and populates the Edit menu commands
edit_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Undo", accelerator="Ctrl + z", command=text_box.edit_undo)
edit_menu.add_command(label="Redo", accelerator="Ctrl + y", command=text_box.edit_redo)
edit_menu.add_command(label="Cut", accelerator="Ctrl + x", command=lambda:cut(False))
edit_menu.add_command(label="Copy", accelerator="Ctrl + c", command=lambda:copy(False))
edit_menu.add_command(label="Paste", accelerator="Ctrl + v", command=lambda:paste(False))
edit_menu.add_command(label="Find", accelerator="Ctrl + f",command=show_find_entry)
edit_menu.add_command(label="Replace", accelerator="Ctrl + r", command=replace_command)
edit_menu.add_command(label="Clear Highlights", command=clear_highlight)

# binds the appropriate key binding to each command shortcut
window.bind('<Control-n>', create_new_file)
window.bind('<Control-o>', open_file)
window.bind('<Control-s>', save)
window.bind("<Control-a>", save_as)
window.bind('<Control-x>', cut)
window.bind('<Control-c>', copy)
window.bind('<Control-v>', paste)
window.bind('<Control-f>', show_find_entry)
window.bind('<Control-r>', replace_command)
text_box.bind('<Key>', mark_unsaved)
text_box.bind('<Tab>', insert_tab)

# calls the quit command when the user attempts to exit the window
window.protocol("WM_DELETE_WINDOW", quit)

window.mainloop()
