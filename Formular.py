"""Step-by-step example: Building a simple Tkinter form in Python.

This script demonstrates how to construct a graphical form using Tkinter
one step at a time. Each section is clearly separated so it can be followed
sequentially while learning how forms are assembled in Python.

The form collects a first name, last name, e-mail address, age and an optional
comment. Whenever the user presses the submit button the inputs are validated
and the data is summarised in a pop-up window.

-------------------------
How to read this example
-------------------------
Every function in this file contains detailed comments that explain what the
code is doing *and why it is done that way*. The idea is to treat the file like
an interactive tutorial:

1. Import the required modules.
2. Define a :class:`dataclass` to hold the submitted form data.
3. Create the main application window.
4. Add form fields (labels + entry widgets).
5. Add a multi-line text widget for free-form comments.
6. Wire up validation and submission logic.
7. Provide feedback to the user after submission.
8. Run the Tkinter event loop.

------------------------
How to show the form window
------------------------
1. Make sure Python 3.10+ is installed. On Windows you can verify this by
   running ``py --version`` in *PowerShell*, on macOS/Linux use
   ``python3 --version``.
2. Open a terminal inside the folder that contains this file.
3. Execute ``python Formular.py`` (or ``python3 Formular.py`` depending on the
   operating system). Tkinter will open a new window titled
   "Schritt-für-Schritt Formular".
4. Keep the editor side-by-side with the application window. When you trigger
   the buttons you can follow along in the source code to see which functions
   are executed.
"""

from __future__ import annotations

# 1. Import the required modules -------------------------------------------------
# ``dataclass`` automatically generates an ``__init__`` method and other handy
# dunder methods so we can focus on the data we want to store.
from dataclasses import dataclass

# Tkinter bundles its widgets in the main ``tkinter`` module and in the themed
# widget set ``tkinter.ttk``. Importing from both allows us to combine classic
# and modern controls. Only the names that we actively use are imported which
# keeps the namespace tidy and readable.
from tkinter import END, LEFT, RIGHT, StringVar, Text, Tk, ttk, messagebox


# 2. Define a dataclass to hold the submitted form data --------------------------
@dataclass
class RegistrationData:
    """Simple container for the form data.

    Each attribute mirrors a single form input. Because the fields are type
    annotated, editors can offer auto-completion and static analysis tools can
    detect type mismatches early.
    """

    first_name: str
    last_name: str
    email: str
    age: int
    comments: str


# 3. Create the main application window -----------------------------------------
def create_main_window() -> Tk:
    """Initialise and configure the top-level Tkinter window.

    Returning the window keeps this function focused on configuration while
    allowing other helpers to continue building on top of it. Think of this as
    the *foundation* of the application.
    """

    # ``Tk()`` starts the Tkinter subsystem and gives us the root window. All
    # other widgets (frames, labels, buttons, ...) will be children of this
    # window. Only a single ``Tk`` instance should exist per application.
    window = Tk()

    # The window title appears in the title bar of the application.
    window.title("Schritt-für-Schritt Formular")

    # ``geometry`` controls the starting size in ``<width>x<height>`` pixels.
    # The form uses a fixed width so that the German labels fit nicely.
    window.geometry("420x360")

    # Prevent the user from resizing the window. This keeps the layout stable
    # which is helpful while learning, because widgets will stay where you
    # expect them to be.
    window.resizable(False, False)

    return window


# 4. Add form fields -------------------------------------------------------------
def build_form_fields(parent: Tk) -> dict[str, StringVar]:
    """Create labelled ``Entry`` widgets and return the associated variables.

    Parameters
    ----------
    parent:
        The widget that should contain the form fields. We expect a Tk window,
        but any ``Frame`` would work as well.

    Returns
    -------
    dict[str, StringVar]
        A mapping from the German label text to the ``StringVar`` object that
        stores the user's input for that row.
    """

    # Mapping of field labels to Tkinter ``StringVar`` instances for data
    # binding. ``StringVar`` acts like a container that keeps track of the
    # entry text. By reading from and writing to the variable we can control the
    # widgets without touching them directly.
    fields: dict[str, StringVar] = {
        "Vorname": StringVar(),
        "Nachname": StringVar(),
        "E-Mail": StringVar(),
        "Alter": StringVar(),
    }

    # ``ttk.Frame`` provides a rectangular container which we use to group the
    # related form controls. ``padding`` adds breathing room around the widgets.
    form_frame = ttk.Frame(parent, padding=20)

    # ``pack`` is one of Tkinter's geometry managers. ``fill='x'`` stretches the
    # frame horizontally so it uses the available width of the main window.
    form_frame.pack(fill="x")

    # ``enumerate`` gives us both the loop index (row) and the key/value pair.
    # For each entry we create one label and one text field.
    for row, (label_text, variable) in enumerate(fields.items()):
        ttk.Label(form_frame, text=label_text + ":").grid(
            column=0,
            row=row,
            sticky="w",  # Align labels to the west (left) edge of the cell.
            padx=(0, 12),  # Add horizontal spacing between label and entry.
            pady=6,  # Vertical space separates each row for readability.
        )
        ttk.Entry(form_frame, textvariable=variable, width=35).grid(
            column=1,
            row=row,
            sticky="ew",  # Expand in both directions to fill the grid cell.
            pady=6,
        )

    # ``columnconfigure`` with ``weight=1`` allows the second column (the entry
    # widgets) to grow when the frame size changes. The first column keeps the
    # labels at their natural width.
    form_frame.columnconfigure(1, weight=1)

    return fields


# 5. Add a multi-line text widget ------------------------------------------------
def build_comments_field(parent: Tk) -> ttk.Frame:
    """Create a labelled text area for free-form comments."""

    # ``LabelFrame`` visually groups widgets and automatically renders a title
    # (in our case "Kommentare"). This signals that the enclosed widgets belong
    # together.
    comments_frame = ttk.LabelFrame(parent, text="Kommentare", padding=12)
    comments_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ``Text`` (from the classic Tk widget set) creates a multi-line text box.
    # ``wrap='word'`` avoids breaking words when the text reaches the end of the
    # line, improving readability. ``Text`` lives in ``tkinter`` rather than in
    # ``tkinter.ttk`` which is why we imported it separately above.
    comments_widget = Text(comments_frame, width=40, height=6, wrap="word")
    comments_widget.pack(fill="both", expand=True)

    # ``Text`` widgets do not accept ``textvariable`` like ``Entry`` does. To
    # make the widget easy to access later on we attach it to the frame. Tkinter
    # widgets are regular Python objects, so we can store additional attributes
    # on them. ``type: ignore`` tells static type checkers that we add this
    # attribute dynamically.
    comments_frame.text_widget = comments_widget  # type: ignore[attr-defined]

    return comments_frame


# 6. Wire up validation and submission logic ------------------------------------
def parse_form_data(
    variables: dict[str, StringVar],
    comments_frame: ttk.Frame,
) -> RegistrationData:
    """Read and validate the user input from the UI widgets.

    The function is kept intentionally small and explicit so that every step is
    easy to trace. When something goes wrong we raise ``ValueError`` with a
    human-readable message. The caller decides how to present this message to
    the user (in this example we use a Tkinter message box).
    """

    # ``.get()`` reads the current value from the ``StringVar``. ``strip()``
    # removes leading/trailing whitespace, which avoids mistakes caused by
    # accidental spaces.
    first_name = variables["Vorname"].get().strip()
    last_name = variables["Nachname"].get().strip()
    email = variables["E-Mail"].get().strip()
    age_text = variables["Alter"].get().strip()

    # Retrieve the multi-line text widget that we stored on the frame earlier.
    comments_widget = comments_frame.text_widget  # type: ignore[attr-defined]

    # ``get("1.0", END)`` reads all characters from the first row/column (1.0)
    # up to the special ``END`` marker. ``strip()`` removes trailing newlines.
    comments = comments_widget.get("1.0", END).strip()

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------
    # Validation is performed step-by-step so the reader understands *what* is
    # being checked and *why* it might fail.

    # Required fields: all text entries except comments must contain something.
    if not all([first_name, last_name, email, age_text]):
        raise ValueError("Bitte füllen Sie alle Pflichtfelder aus.")

    # A very small email check to demonstrate custom validation logic.
    if "@" not in email or "." not in email:
        raise ValueError("Bitte geben Sie eine gültige E-Mail-Adresse ein.")

    try:
        # Convert the text to an integer. ``int`` will raise ``ValueError`` if
        # the string does not contain a valid whole number (e.g. letters).
        age = int(age_text)
        if age <= 0:
            # Manually trigger ``ValueError`` for non-positive ages.
            raise ValueError
    except ValueError as exc:
        # ``from exc`` keeps the original stack trace which helps with debugging
        # if the code is later expanded.
        raise ValueError("Alter muss eine positive Zahl sein.") from exc

    # Pack the validated values into a ``RegistrationData`` instance. Using a
    # dataclass keeps related attributes bundled together and provides useful
    # ``repr``/``eq`` implementations for free.
    return RegistrationData(
        first_name=first_name,
        last_name=last_name,
        email=email,
        age=age,
        comments=comments,
    )


def handle_submit(variables: dict[str, StringVar], comments_frame: ttk.Frame) -> None:
    """Validate the form data and provide feedback to the user."""

    try:
        # ``parse_form_data`` raises ``ValueError`` for invalid user input. We
        # catch it here and translate the message into a user-friendly dialog.
        data = parse_form_data(variables, comments_frame)
    except ValueError as error:
        # ``showerror`` creates a modal dialog that blocks interaction with the
        # main window until the user closes the message box. This ensures that
        # the user sees the error and can correct the input immediately.
        messagebox.showerror("Fehler", str(error))
        return

    # 7. Provide feedback to the user ------------------------------------------
    # ``str.format`` fills in the placeholders with the attributes of our
    # dataclass. Using ``{0.first_name}`` keeps the template easy to read.
    message = (
        "Vielen Dank, {0.first_name} {0.last_name}!\n\n"
        "Wir haben Ihre Daten erhalten und melden uns unter {0.email}."
    ).format(data)

    # ``showinfo`` displays a green info icon that confirms the success.
    messagebox.showinfo("Erfolg", message)

    # After a successful submission we call ``reset_form`` so the form is ready
    # for the next set of inputs.
    reset_form(variables, comments_frame)


def reset_form(variables: dict[str, StringVar], comments_frame: ttk.Frame) -> None:
    """Clear all widgets so the form starts fresh."""

    for variable in variables.values():
        # Setting the ``StringVar`` to the empty string automatically clears the
        # corresponding entry field on screen.
        variable.set("")

    # ``delete`` removes characters from the text widget. ``END`` is inclusive,
    # therefore using ``END`` twice ensures the entire content is removed.
    comments_frame.text_widget.delete("1.0", END)  # type: ignore[attr-defined]


# 8. Run the Tkinter event loop --------------------------------------------------
def main() -> None:
    """Assemble the GUI and start the Tkinter event loop."""

    # Step 1: create the main window that everything else will live inside of.
    window = create_main_window()

    # Step 2: build the form inputs and keep references to their variables.
    variables = build_form_fields(window)

    # Step 3: add the multi-line comments field beneath the regular entries.
    comments_frame = build_comments_field(window)

    # Step 4: create a horizontal frame for the action buttons.
    button_frame = ttk.Frame(window, padding=(20, 0, 20, 20))
    button_frame.pack(fill="x")

    # ``ttk.Button`` is connected to a ``command`` callback. Lambda allows us to
    # pass the current variables without defining a separate function.
    submit_button = ttk.Button(
        button_frame,
        text="Absenden",
        command=lambda: handle_submit(variables, comments_frame),
    )
    submit_button.pack(side=LEFT, expand=True, fill="x", padx=(0, 10))

    reset_button = ttk.Button(
        button_frame,
        text="Zurücksetzen",
        command=lambda: reset_form(variables, comments_frame),
    )
    reset_button.pack(side=RIGHT, expand=True, fill="x")

    # ``mainloop`` hands control over to Tkinter. The method keeps running until
    # the user closes the window. All button clicks, key presses and redraws are
    # processed inside this loop.
    window.mainloop()


if __name__ == "__main__":
    main()