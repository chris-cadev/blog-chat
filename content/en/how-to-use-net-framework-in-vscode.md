---
title: "How to use .NET Framework in VS Code"
slug: how-to-use-net-framework-in-vscode
description: "A ready-to-use EditorConfig and web.config for .NET development in VS Code."
tags:
  - dotnet
  - vscode
  - tools
created: '2025-11-26'
updated: '2026-09-21'
lang: en
lang_group: how-to-use-net-framework-in-vscode
---

At a factory in Tijuana, everything ran on Microsoft and IBM — .NET, C#, Windows Server. Visual Studio was the standard IDE, but loading it with large solutions was heavy. VS Code was the lightweight alternative: it started fast, didn't eat RAM, and for everyday tasks like editing configs or debugging scripts, it was more than enough.

What was missing was an `EditorConfig` that unified formatting rules between both editors. Without it, each one formatted its own way and diffs were a mess. Here's the one that worked, ready to copy.

## EditorConfig essentials

Start with the global rules: UTF-8 charset, consistent newlines, and indentation per file type. This ensures VS and VS Code share the same base rules.

```toml
# Top-most EditorConfig file
root = true

# All files
[*]
charset = utf-8
insert_final_newline = true
trim_trailing_whitespace = true

# Code files
[*.{cs,csx,vb,vbx}]
indent_size = 4
indent_style = space
tab_width = 4

# XML project files
[*.{csproj,vbproj,vcxproj,vcxproj.filters,proj,projitems,shproj}]
indent_size = 2

# XML config files
[*.{props,targets,ruleset,config,nuspec,resx,vsixmanifest,vsct}]
indent_size = 2

# JSON files
[*.json]
indent_size = 2

# YAML files
[*.{yml,yaml}]
indent_size = 2

# Shell scripts
[*.sh]
end_of_line = lf

# Batch scripts
[*.{cmd,bat}]
end_of_line = crlf
```

## C# formatting rules

C# formatting rules prevent unnecessary diffs between editors. The most important part: where braces go, how blocks are indented, and spaces around operators.

```toml
[*.cs]
indent_size = 4
indent_style = space
tab_width = 4

# New line preferences
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true
csharp_new_line_before_members_in_object_initializers = true
csharp_new_line_before_members_in_anonymous_types = true
csharp_new_line_between_query_expression_clauses = true

# Indentation preferences
csharp_indent_case_contents = true
csharp_indent_switch_labels = true
csharp_indent_labels = flush_left

# Space preferences
csharp_space_after_cast = false
csharp_space_after_keywords_in_control_flow_statements = true
csharp_space_between_parentheses = false
csharp_space_before_colon_in_inheritance_clause = true
csharp_space_after_colon_in_inheritance_clause = true
csharp_space_around_binary_operators = before_and_after
csharp_space_after_comma = true
csharp_space_before_comma = false
csharp_space_after_semicolon_in_for_statement = true
csharp_space_before_semicolon_in_for_statement = false
```

## Naming conventions

Naming conventions are critical in a team. If everyone follows the same rules, code reviews focus on logic, not style.

```toml
# Async methods should end with Async
dotnet_naming_rule.async_methods_end_in_async.severity = warning
dotnet_naming_rule.async_methods_end_in_async.symbols = async_methods
dotnet_naming_rule.async_methods_end_in_async.style = end_in_async

dotnet_naming_symbols.async_methods.applicable_kinds = method
dotnet_naming_symbols.async_methods.applicable_accessibilities = *
dotnet_naming_symbols.async_methods.required_modifiers = async

dotnet_naming_style.end_in_async.required_suffix = Async
dotnet_naming_style.end_in_async.capitalization = pascal_case

# Interfaces must start with I
dotnet_naming_rule.interface_should_be_begins_with_i.severity = warning
dotnet_naming_rule.interface_should_be_begins_with_i.symbols = interface
dotnet_naming_rule.interface_should_be_begins_with_i.style = begins_with_i

dotnet_naming_symbols.interface.applicable_kinds = interface
dotnet_naming_symbols.interface.applicable_accessibilities = *

dotnet_naming_style.begins_with_i.required_prefix = I
dotnet_naming_style.begins_with_i.capitalization = pascal_case

# Types should be PascalCase
dotnet_naming_rule.types_should_be_pascal_case.severity = warning
dotnet_naming_rule.types_should_be_pascal_case.symbols = types
dotnet_naming_rule.types_should_be_pascal_case.style = pascal_case

dotnet_naming_symbols.types.applicable_kinds = class,struct,interface,enum
dotnet_naming_symbols.types.applicable_accessibilities = *

dotnet_naming_style.pascal_case.capitalization = pascal_case

# Private fields should be _camelCase
dotnet_naming_rule.private_fields_with_underscore.severity = warning
dotnet_naming_rule.private_fields_with_underscore.symbols = private_fields
dotnet_naming_rule.private_fields_with_underscore.style = prefix_underscore

dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private

dotnet_naming_style.prefix_underscore.required_prefix = _
dotnet_naming_style.prefix_underscore.capitalization = camel_case
```

## Diagnostic severities

These are the diagnostic rules that actually matter day-to-day. IDE rules handle the visual stuff, CA rules handle code quality. The full config has over 60 rules — use the ones you need.

```toml
# IDE diagnostics
dotnet_diagnostic.IDE0001.severity = warning # Simplify name
dotnet_diagnostic.IDE0002.severity = warning # Simplify member access
dotnet_diagnostic.IDE0003.severity = warning # Remove this or Me qualification
dotnet_diagnostic.IDE0004.severity = warning # Remove unnecessary cast
dotnet_diagnostic.IDE0005.severity = warning # Remove unnecessary import
dotnet_diagnostic.IDE0051.severity = warning # Remove unused private member
dotnet_diagnostic.IDE0052.severity = warning # Remove unread private member
dotnet_diagnostic.IDE0055.severity = warning # Fix formatting
dotnet_diagnostic.IDE0059.severity = warning # Unnecessary assignment
dotnet_diagnostic.IDE0060.severity = warning # Remove unused parameter

# Code quality rules
dotnet_diagnostic.CA1001.severity = warning # Types that own disposable fields should be disposable
dotnet_diagnostic.CA1060.severity = warning # Move P/Invokes to NativeMethods class
dotnet_diagnostic.CA1061.severity = warning # Do not hide base class methods
dotnet_diagnostic.CA1063.severity = warning # Implement IDisposable correctly
dotnet_diagnostic.CA1065.severity = warning # Do not raise exceptions in unexpected locations
dotnet_diagnostic.CA1821.severity = warning # Remove empty finalizers
dotnet_diagnostic.CA2002.severity = warning # Do not lock on objects with weak identity
dotnet_diagnostic.CA2100.severity = warning # Review SQL queries for security vulnerabilities
dotnet_diagnostic.CA2200.severity = warning # Rethrow to preserve stack details
dotnet_diagnostic.CA2216.severity = warning # Disposable types should declare finalizer
dotnet_diagnostic.CA2229.severity = warning # Implement serialization constructors
dotnet_diagnostic.CA2235.severity = warning # Mark all non-serializable fields
```

## web.config: language encoding

If your app handles internationalization or needs a specific culture, the `web.config` must declare encoding and culture explicitly. Without this, ASP.NET uses the server's culture — which in a factory in Tijuana probably isn't the one you want.

```xml
<system.web>
  <globalization
      fileEncoding="utf-8"
      requestEncoding="utf-8"
      responseEncoding="utf-8"
      culture="es-ES"
      uiCulture="es-ES" />
</system.web>
```

## Getting the full config

This post covers the most useful sections. The full config has over 300 lines with all the naming, formatting, and diagnostics rules for .NET.

Copy the sections you need, or download the full config from the project repository. The important thing is that VS and VS Code share the same `EditorConfig` — that's what prevents the formatting diffs that drive you crazy during code review.
