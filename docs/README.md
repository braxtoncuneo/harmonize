
# Welcome!

If you're reading this document, you're likely bursting with excitement to start updating the Harmonize documentation!

At the moment we have **two options** to help you get started. You can take a look and choose which one you need.


---


### Option 1 | I'm ready to start writing pages!

**Difficulty:** Easy

If you want to get started right away with writing some pages, take a look at the **`Content`** folder under `docs/Content`.

Each content-containing page is written in `MDX`, an extended version of Markdown that lets you embed special web-focused contend (in the `JSX` format).

> [!NOTE]
>
> These types of pages are intended to be used for guides, tutorials, and longer-form prose. They can be used to supplement the automatically documented library API, but do not directly influnce the behavior of the API's generation. If you need to customize API generation, take a look a the second customization option. 

Here is how pages work:
- **First, Frontmatter**
    
    Pages begin with a frontmatter title that provides structured information to the website framework its content.

    ```
    ---
    title: Your Page Title Goes Here
    description: Your Page Description Goes Here
    ---
    ```

- **Then, Markdown (MD) Content**

    The page frontmatter is followed by the actual content of your page, formatted in Markdown.

<br />

For more information on how to organize your pages, you can take a look at the **[Fumadocs page conventions guide](https://fumadocs.dev/docs/ui/page-conventions)**. There are also some special Fumadocs-specific formatting components you can use that are demonstrated in the pages under the `(gettingStarted)` folder.


> [!WARNING]
>
> Make sure not to delete the `cppAPI` and `pythonAPI` folders!
> While they might not look like they're doing much, they are in fact placeholders for the automatically generated API.
>
> It is safe, however, to update the `meta.json` in these folders. This file customizes how the API appears in the left page navigation sidebar.


---

### Option 2 | I'd like to customize the API Documentation Build Process or the Configuration of the Fumadocs/Next.js Site Builder

**Difficulty:** A Bit More Involved

Customizing the API documentation build process or the Fumadocs/Next.js is a bit more involved, and requires an understanding of how the documentation is organized and built. This is currently done using **three** primary tools. Each tool has configuration files that will allow you to tune its piece of the build. These files are located in the folders that corrospond to the names of the tools.

Each tool is used as follows:

1. **Doxygen**

    - Doxygen is used to generate API documentation for C++ Code.
    - Reads C++ Source Code ****->**** Exports as XML

2. **Sphinx**

    - Sphinx is used to generate API documentation for Python Code. Extensions also allow it to ingest and combine this information with Doxygen-generated APIs.

    - Reads C++ and Python Source Code ****->**** Exports Structured Pages in JSON

    A.) **Breathe**

    - Breathe is a third-party Sphinx extension that allows Sphinx to ingest Doxygen XML exports in a way that the Sphinx engine understands.

    - Ingests Doxygen XML Exports ****->**** Exposes Structured Information to Sphinx

    B.) **Sphinx-Autodoc2**

    - `sphinx-autodoc2` is a Sphinx extension that allows Sphinx to generate API documentation from the static files of a Python project. Crucially, it provides Sphinx with the ability to parse Python docstrings as Markdown.

    - Reads Python Source Code ****->**** Parses Markdown Docstrings and Generated Files to Let Sphinx Know What to Do

3. **Fumadocs**

    - Fumadocs is a website template/toolkit designed to assist developers with publishing clean and modern documentation. It is built upon Next.js, a JavaScript framework that helps you to create websites and webapps.

        - Next.js websites can be run using a server (for more involved webapps that might require lots of data processing). If you don't need certain server-based features, you can export your site as a *static site*. When you do this, Next.js generates files representing a snapshot of the entire site. Since static files are relatively easy and inexpensive to share (as compared to dynamic websites where a server needs to process things before each pages is returned), many companies host these files for free (letting you run a free website).

            This documentation *is* exported and published as a static site on GitHub Pages. The build process is triggered on GitHub pushes, and is controlled by the build `Workflow` under `.github/workflows/documentation.yml`

    - Natively, Fumadocs only supports `MDX` (Markdown) content. A good amount of work has gone into adapting the content of Sphinx JSON files into a format Fumadocs can understand. To learn more about how this works, take a look at the `README.md` in the root of the Fumadocs/Next.js project. 
    
    - This documentation site uses the Fumadocs/Next.js Content Collections setup.

    - Reads `MDX` (Markdown) files and Ingests Sphinx JSON Exports ****->**** Generates a Full HTML Documentation Website Ready for Publishing on the Internet

<br />

# Good luck, and have fun with your documenting!