from dataclasses import dataclass, field
from drafter import *
from bakery import assert_equal as ae

add_website_css("""
.dark-theme {
    background-color: #121212;
    color: #f0f0f0;
    min-height: 100vh;
    padding: 20px;
}
.dark-theme input, .dark-theme select {
    background-color: #2a2a2a;
    color: #ffffff;
    border: 1px solid #555555;
}
.dark-theme button {
    background-color: #333333;
    color: #ffffff;
    border: 1px solid #666666;
}
.light-theme {
    background-color: #ffffff;
    color: #111111;
    min-height: 100vh;
    padding: 20px;
}
""")


# -----Dataclasses-----

@dataclass
class Assignment:
    max_points: int
    category: str
    points: int  # likely/earned points


@dataclass
class Category:
    name: str
    weight: float
    total_points: int
    assignments: list[Assignment] = field(default_factory=list)


# -----Drafter-----
@dataclass
class State:  # Stores info
    categories: list[Category]
    assignments: list[Assignment]
    current_grade: float
    dark_mode: bool
    editing_cat_index: int

@route
def index(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    return Page(state, [
        Div([
            "Choose a calculator\n",
            Button("Category Maker", "cat_chooser"),
            Button("Edit Categories / Assignments", "edit_menu"),
            Button("Grade Calculator", "calculator"),
            Button("Extra Credit Calculator", "ec_calculator"),
            Button("Dark Mode", "toggle_dark_mode"),
        ], classes=theme_class)
    ])

@route
def toggle_dark_mode(state: State) -> Page:
    state.dark_mode = not state.dark_mode
    return index(state)


@route
def cat_chooser(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    return Page(state, [Div([
        Div(Header("Choose a category making method"), text_align="center"),
        Div([
            Button("Have point information", "cat_maker"),
            Button("Don't have point information", "man_cat_maker")
        ], display="flex", justify_content="space-between", align_items="center"),
        Div(Button("Home", "index"), justify_content="right")
    ], classes=theme_class)])


# -----Manual Category Maker-----

@route
def man_cat_maker(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    return Page(state, [Div([
        Div([
            Div(["Number of assignments ->", TextBox("assign_num", "", type="number")]),
            Button("Next", "man_cat_maker2")
        ], display="flex", justify_content="space-between", align_items="center"),
        Div(Button("Home", "index"), justify_content="right")
    ], classes=theme_class)])


@route
def man_cat_maker2(state: State, assign_num: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    components = [
        "\n", "Category name ->", TextBox("cat_name"), "\n",
        "Category weight (%) ->", TextBox("cat_weight", type="number"), "\n\n"
    ]
    for i in range(int(assign_num)):
        components.append(f"Assignment {i + 1} Max Points -> ")
        components.append(TextBox(f"max_points_{i}", "", type="number"))
        components.append(f" Earned/Expected Points -> ")
        components.append(TextBox(f"points_{i}", "", type="number"))
        components.append("\n")

    components.append(Button("Submit All", "man_cat_maker3"))
    return Page(state, [Div([
        Div(["Number of assignments ->", TextBox("assign_num", assign_num)]), "\n",
        components,
    ], classes=theme_class)])


@route
def man_cat_maker3(state: State, assign_num: str, cat_name: str, cat_weight: str, **kwargs: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    total = 0
    cat_assignments = []

    for i in range(int(assign_num)):
        max_val = int(kwargs.get(f"max_points_{i}") or "0")
        earned_val = int(kwargs.get(f"points_{i}") or "0")
        total += max_val

        new_assignment = Assignment(max_val, cat_name, earned_val)
        state.assignments.append(new_assignment)
        cat_assignments.append(new_assignment)

    new_category = Category(cat_name, float(cat_weight) / 100, total, cat_assignments)
    state.categories.append(new_category)

    return Page(state, [
        Div([
            f"Saved category '{cat_name}' with {assign_num} assignments ({total} total points).\n",
            Button("Back to Home", "index")
        ], classes=theme_class)
    ])


# -----Standard Category Maker-----

@route
def cat_maker(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    return Page(state, [
        Div([
            Div(Header("Make a grading category"), text_align="center"), "\n",
            "Category Name ->", TextBox("cat_name", ""), "\n",
            "Category Weight (%) ->", TextBox("cat_weight", "", type="number"), "\n",
            "Category Points ->", TextBox("cat_points", "", type="number"), "\n\n",
            Div([Button("Save", "cat_saver"), Button("Home", "index")],
                display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])


@route
def cat_saver(state: State, cat_name: str, cat_weight: str, cat_points: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    state.categories.append(Category(cat_name, float(cat_weight) / 100, int(cat_points), []))
    return Page(state, [
        Div([
            Div(Header("Make a grading category"), text_align="center"), "\n",
            "Category Name ->", TextBox("cat_name", cat_name), "\n",
            "Category Weight ->", TextBox("cat_weight", cat_weight), "\n",
            "Category Points ->", TextBox("cat_points", cat_points), "\n\n",
            Div([Button("Save", "cat_saver"), "Saved!", Button("Home", "index")],
                display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])


# -----Edit Categories & Assignments-----

@route
def edit_menu(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    if not state.categories:
        return Page(state, [
            Div([
                Header("Edit Categories & Assignments"),
                "No categories created yet.\n",
                Button("Create a Category", "cat_chooser"),
                Button("Home", "index")
            ], classes=theme_class)
        ])

    cat_names = [cat.name for cat in state.categories]
    return Page(state, [
        Div([
            Header("Edit Categories & Assignments"),
            "Select a category to edit -> ",
            SelectBox("selected_cat", cat_names), "\n\n",
            Div([
                Button("Edit Selected", "edit_category_page"),
                Button("Home", "index")
            ], display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])


@route
def edit_category_page(state: State, selected_cat: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    target_cat = None
    for idx, cat in enumerate(state.categories):
        if cat.name == selected_cat:
            target_cat = cat
            state.editing_cat_index = idx
            break

    if target_cat is None:
        return edit_menu(state)

    components = [
        Header(f"Editing Category: {target_cat.name}"),
        "Category Name -> ", TextBox("new_name", target_cat.name), "\n",
        "Category Weight (%) -> ", TextBox("new_weight", str(round(target_cat.weight * 100, 2)), type="number"), "\n",
        "Category Total Points -> ", TextBox("new_total_points", str(target_cat.total_points), type="number"), "\n\n"
    ]

    if target_cat.assignments:
        components.append(Header("Assignments in this Category"))
        components.append("Note: Saving will automatically recalculate total points from these assignments.\n\n")
        for i, assign in enumerate(target_cat.assignments):
            components.append(f"Assignment {i + 1} Max Points -> ")
            components.append(TextBox(f"assign_max_{i}", str(assign.max_points), type="number"))
            components.append(" Earned Points -> ")
            components.append(TextBox(f"assign_pts_{i}", str(assign.points), type="number"))
            components.append("\n")

    components.append("\n")
    components.append(Div([
        Button("Save Changes", "save_edited_category"),
        Button("Cancel", "edit_menu"),
        Button("Home", "index")
    ], display="flex", justify_content="space-between", align_items="center"))

    return Page(state, [Div(components, classes=theme_class)])


@route
def save_edited_category(state: State, new_name: str, new_weight: str, new_total_points: str, **kwargs: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    cat = state.categories[state.editing_cat_index]
    old_name = cat.name

    cat.name = new_name
    cat.weight = float(new_weight) / 100

    # Update assignments inside this category if any exist
    if cat.assignments:
        recalculated_total = 0
        for i, assign in enumerate(cat.assignments):
            new_max = int(kwargs.get(f"assign_max_{i}") or assign.max_points)
            new_pts = int(kwargs.get(f"assign_pts_{i}") or assign.points)
            assign.max_points = new_max
            assign.points = new_pts
            assign.category = new_name
            recalculated_total += new_max
        cat.total_points = recalculated_total
    else:
        cat.total_points = int(new_total_points)

    # Also update category name reference in global state.assignments
    for assign in state.assignments:
        if assign.category == old_name:
            assign.category = new_name

    return Page(state, [
        Div([
            f"Successfully updated '{cat.name}'!\n",
            Button("Edit Another", "edit_menu"),
            Button("Home", "index")
        ], classes=theme_class)
    ])


# -----Grade Calculator-----

@route
def calculator(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    categories = [category.name for category in state.categories]
    return Page(state, [
        Div([
            Div(Header("Grade Calculator"), text_align="center"),
            Div([
                Div(["Category ->", SelectBox("cat_name", categories), Span("All Categories must be made", color="gray")]),
                Button("Make a category", "cat_chooser")
            ], display="flex", align_items="center", justify_content="space-between"),
            "Assignment max points ->", TextBox("max_points"), "\n",
            "Assignment expected points ->", TextBox("points"), "\n",
            "Current grade ->", TextBox("grade"), "\n",
            Div([Button("Calculate", "calculated"), Button("Home", "index")],
                display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])


@route
def calculated(state: State, max_points: str, points: str, cat_name: str, grade: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    cat_tot_percent = 0
    score = (int(points) / int(max_points)) * 100
    cat = None
    for category in state.categories:
        cat_tot_percent += category.weight
        if category.name == cat_name:
            cat = category

    assign_weight = cat.weight * int(max_points) / cat.total_points
    unkw = cat_tot_percent - assign_weight
    Grade = ((float(grade) * unkw) + (score * assign_weight)) / (unkw + assign_weight)

    return Page(state, [
        Div([
            Div(Header("Grade Calculator"), text_align="center"),
            Div([
                Div(["Category ->", TextBox("cat_name", cat_name), Span("All Categories must be made", color="gray")]),
                Button("Make a category", "cat_chooser")
            ], display="flex", align_items="center", justify_content="space-between"),
            "Assignment max points ->", TextBox("max_points", max_points), "\n",
            "Assignment expected points ->", TextBox("points", points), "\n",
            "Current grade ->", TextBox("grade", grade), "\n",
            Button("Re-Calculate", "calculated"),
            Div(["Updated grade -> ", str(round(Grade, 2)), "%", Button("Home", "index")],
                display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])

# -----Extra Credit Calculator-----

@route
def ec_calculator(state: State) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    if not state.categories:
        return Page(state, [
            Div([
                Header("Extra Credit Calculator"),
                "You need to create at least one category first.\n",
                Button("Make a Category", "cat_chooser"),
                Button("Home", "index")
            ], classes=theme_class)
        ])

    categories = [category.name for category in state.categories]
    return Page(state, [
        Div([
            Div(Header("Extra Credit Calculator"), text_align="center"),
            Div([
                Div(["Category -> ", SelectBox("cat_name", categories)]),
                Button("Make a category", "cat_chooser")
            ], display="flex", align_items="center", justify_content="space-between"), "\n",
            "Extra credit points earned -> ", TextBox("ec_points", "", type="number"), "\n",
            "Current overall grade (%) -> ", TextBox("grade", "", type="number"), "\n\n",
            Div([
                Button("Calculate Extra Credit", "ec_calculated"),
                Button("Home", "index")
            ], display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])


@route
def ec_calculated(state: State, cat_name: str, ec_points: str, grade: str) -> Page:
    theme_class = "dark-theme" if state.dark_mode else "light-theme"
    categories = [category.name for category in state.categories]

    cat = None
    cat_tot_percent = 0.0
    for category in state.categories:
        cat_tot_percent += category.weight
        if category.name == cat_name:
            cat = category

    if cat is None or cat.total_points == 0:
        return Page(state, [
            Div([
                "Error: Category has 0 total points. Please edit the category points first.\n",
                Button("Edit Categories", "edit_menu"),
                Button("Home", "index")
            ], classes=theme_class)
        ])

    # Extra credit adds points to the numerator without increasing total possible points
    ec_val = float(ec_points)
    current_grade = float(grade)
    
    # Percentage boost inside that specific category, scaled by its weight relative to active categories
    category_boost = (ec_val / cat.total_points) * 100
    weighted_boost = category_boost * (cat.weight / cat_tot_percent)
    new_grade = current_grade + weighted_boost

    return Page(state, [
        Div([
            Div(Header("Extra Credit Calculator"), text_align="center"),
            Div([
                Div(["Category -> ", SelectBox("cat_name", categories, default_value=cat_name)]),
                Button("Make a category", "cat_chooser")
            ], display="flex", align_items="center", justify_content="space-between"), "\n",
            "Extra credit points earned -> ", TextBox("ec_points", ec_points, type="number"), "\n",
            "Current overall grade (%) -> ", TextBox("grade", grade, type="number"), "\n\n",
            Button("Re-Calculate", "ec_calculated"), "\n\n",
            f"Category Boost: +{round(category_boost, 2)}%\n",
            f"Overall Grade Boost: +{round(weighted_boost, 2)}%\n",
            Div([
                f"Updated Grade -> {round(new_grade, 2)}%",
                Button("Home", "index")
            ], display="flex", justify_content="space-between", align_items="center")
        ], classes=theme_class)
    ])

set_website_title("Grade Calculator")
set_site_information(
    author="Ryan Nevard",
    description="Calculate how your grade will change.",
    sources="",
    planning=[""],
    links=[""]
)

hide_debug_information()
set_website_framed(False)

start_server(State([], [], 0.0, False, 0))

