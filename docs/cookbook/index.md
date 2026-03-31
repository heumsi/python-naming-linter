# Cookbook

The cookbook provides ready-to-use recipes for common naming convention scenarios. Each recipe shows a complete configuration, a violation example, and a passing example so you can adapt it to your project immediately.

## Recipes

| Recipe | Description |
|--------|-------------|
| [Bool Method Prefix](./bool-method-prefix.md) | Require `is_`, `has_`, or `should_` prefix on functions that return `bool` |
| [Exception Naming](./exception-naming.md) | Enforce a structured suffix pattern on exception class names |
| [Attribute Matches Type](./attribute-matches-type.md) | Require attribute names to match their type annotation in snake_case |
| [Module Matches Class](./module-matches-class.md) | Require module filenames to match the primary class they contain |
| [Layer-Based Rules](./layer-based-rules.md) | Apply different rule sets to different layers of your codebase |
| [Constant Upper Case](./constant-upper-case.md) | Require module-level constants to use UPPER_CASE |
| [Decorator Filtering](./decorator-filtering.md) | Apply naming rules only to functions or classes with a specific decorator |
