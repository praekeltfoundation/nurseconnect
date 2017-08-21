FED PROJECT STRUCTURE

FED Automation
nurseconnect/fed/

RUNNING FED

Shared styles setting on nurseconnect/nurseconnect/settings/base.py
STATICFILES_DIRS = [
    join(PROJECT_ROOT, "/dist"),
]

DJANGO PROJ Source-code
nurseconnect/nurseconnect

RUNNING Project
Gulp
  - SASS automation
  - SASS Lint
    * Object options for your project rules on Configfile.js?
    SASS Lint has default configuration rules
    * if you provide one it attempts to merge everything except for the files on section below.
    If you pass options directly into the plugin they take precedence.
    sassLint config order: options > config file > SassLint default included config.

    * You can disable this behaviour by setting merge-default-rules to false within the options.options object that you pass to gulp-sass-lint or you can include it in your config file options that you can pass into gulp-sass-lint with options.configFile.

  - Icons => Research further
  - .editorconfig
    # EditorConfig helps developers define and maintain consistent
    # coding styles between different editors and IDEs
    # editorconfig.org

  LINT rules
  -   # Extends
      # Mixins
      # Line Spacing
      # Disallows
      # Nesting
      # Name Formats
      # Style Guide
      # Inner Spacing
      # Final Items

  RESET STYLES
  @import "../../../../../node_modules/sanitize.css/sanitize";
  sassConfig - 'node_modules/breakpoint-sass/stylesheets/'

  HOW DOES grunticon integration with gulp generated svgs?
  http://www.grunticon.com/

  SASS STRUCTURE
  http://thesassway.com/beginner/how-to-structure-a-sass-project


  # Nurse Connect - project breakdown

  ## SVGS

   300px wide. close crop, icons should be in consistent ratio containers where possible. all #213d55 (Regal Blue) expanded properly (check with kgosi, peter, chris, or jw if your not sure how):

  - logo (2 tone)
  - icon-search
  - icon-profile
  - icon-burger
  - icon-users (for the user count indicator)
  - icon-comments
  - icon-star
  - icon-location
  - icon-exclamation
  - icon-question-mark
  - icon-chevron-left
  - icon-chevron-right
  - icon-plus
  - icon-minus (? don't see one in the designs, is it necessary)
  - icon-pills
  - icon-clinic
  - icon-clipboard
  - icon-baby
  - icon-children
  ... think thats all of them


  ## COLORS:

  - blue-tranquil: #dae8eb
      background 1st lvl
  - blue-spindle: #c0d6dd
      background 2nd lvl
  - white: #ffffff
      background 3rd lvl, button text
  - blue-pelorous: #2d9ec5 (ci, links and interactive color)
      h2,buttons
  - orange-bittersweet: #ff6655 (ci first level importance)
      h1,qoutes,section catagories/tags, first level icons
  - blue-regal: #213d55 (ci second level importance)
      inactive state, secondary icons, p
  - grey-light-slate: #7e93a0 (ci third level importance) == 50% opacity of blue-regal
      descriptive text, radio labels, nested background state

  ## COMPONENTS:

  - logo
  - navigation
  - breadcrumb
  - listing view:
    - results or catagory,  articles list (h2, desc, image/icon)
    - catagories/sub-catagories (just h2 and icon)
    - with subcatagories
  -detail view:
    - create group

  - form-fields
    - input field
    - input field
    - pill input with icon
    - radio buttons
    - dropdowns/selectbox
    - checkbox (as a toggle icon)
  - pill button
  - progress bar
  - dashboard
    - large number
    - medium number
    - graph over months
  - square img/icon
  - content sections:
      background 1/2/3
  - blocks:
    - well (white with round corners)
    - list block
    - image block
    - text block


STYLEGUIDE
nurseconnect/styleguide

RUNNING Styleguides


TO DO

- Footer Back to Top button
  => JS enabled on Desktop and Smartphone
- Menu hover - to use selected icon
- Selected section menu static [page]

- Add section, subsection, article pages flow [section_page.html] & [article_page.html]
