# Code conventions

Ruff and pyright own formatting, import order, typing syntax and docstring format. Do not restate thoses rules, dont't argue with them, and don't add `# noqa` comments to get past those rules.

## Tooling assumptions
- Ruff is the only linter and formater. `ruff.toml` at the repo root is the source of truth for all formatting and linting rules. Don't edit it to get past lint failure; fix the code.
- pyright runs in `standard` mode. Annotate every parameter and every return, including `-> None`.

## Layers
The project is organized in layers. The boundary between layers is defined by the import rules and user of the layer is (dependency inversion principle).
- **Domain** (core): raises, returns data and never prints. It defines the business logic and the data entities. It can only import from the domain layer. It is used by the application layer.
- **Application**: orchestrates the domain layer and implements use cases. It can import from the domain layer and from the application layer. It is used by the presentation layer and by developers wanting to use the domain layer.
- **Presentation**: implements the user interface. It can import from the application layer and from the presentation layer. It is used by the end user.

## Import
- Import the module and qualify the use: `import dataclasses` then `@dataclasses.dataclass`. Same for `abc`, `enum`, `pathlib`, etc
- Relative imports within a subpackage, absolute imports across subpackages. Never `...`.
- Prioritize `pathlib` over `os`.

## Data
- Use `dataclass` for data entities. They are immutable by default. Drop the `frozen=True` only with stated reason.
- Anything peristent or crossing a module or a layer's boundary is a dataclass. Never a bare dict. Avoid accessing attributes (or values) with hardcoded strings.

## Errors
- Domain errors get a custom exception class in the domain layer. They are raised by the domain layer and caught by the application layer. The application layer can then decide how to handle them.
- Use standard library exceptions only when they are appropriate: `ValueError` for a bad argument, `FileNotFoundError` for a missing file, etc.
- Never return `None` to mean "not found". Raise.

## Structure
- src-layout
- Single responsibility principle: one per class, function or module. High number of line in a components may indicate too many responsibilities. Split them.
- KISS: Keep It Simple, Stupid. Favor minimal, simple, explicit and readable code.
- Explicit conditions: `has_views = video.views > 0; if has_views: do_something();`

## Docstrings and comments
- Public class and public function docstring are required. Private helpers get one only when the mechanics are non-obvious.
- Comments explain why. A comment restating the code gets deleted.
- Do not leave commented-out code. Delete it. Git remembers it if needed.
- `# TODO` comments needs enough context to still make sense in a year. If the entire body of a function is a `# TODO`: it's an unimplemented function, raise `NotImplementedError` instead.

## Tests
- If ask for code and don't mention tests, ask wheter to write them. If tests are needed, a new behavior in `src/` arrives with a test in `tests/`.
- Name the test rather than docstringing it: `test_<subject>_<condition>`. Reserve a `_raises` suffix for test whose whole point is the exception.
- Patches in unit tests or in low level layers may indicate code smell. Use it if unavoidable, otherwise fix the code.

# Don't do these unpromted
- No README or docs edits I didn't ask for.
