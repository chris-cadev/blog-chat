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

# How to use .NET Framework in VS Code

En una fábrica en Tijuana, todo corría sobre Microsoft y IBM — .NET, C#, Windows Server. Visual Studio era el IDE estándar, pero cargarlo con soluciones grandes pesaba. VS Code era la alternativa ligera: arrancaba rápido, no comía RAM, y para tareas cotidianas como editar configs o debugear scripts, sobraba.

Lo que faltaba era un `EditorConfig` que unificara las reglas de formato entre ambos editores. Sin él, cada uno formateaba a su manera y los diffs eran un caos. Aquí está el que funcionó, listo para copiar.

## EditorConfig essentials

Empieza con las reglas globales: charset UTF-8, newlines consistentes, y indentación por tipo de archivo. Esto asegura que VS y VS Code compartan las mismas reglas base.

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

Las reglas de formato de C# evitan diffs innecesarios entre editores. Lo más importante: dónde van los braces, cómo se indentan los blocks, y los espacios alrededor de operadores.

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

Las naming conventions son críticas en equipo. Si todos siguen las mismas reglas, los code reviews se enfocan en lógica, no en estilo.

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

Estas son las reglas de diagnóstico que realmente importan en el día a día. Las IDE van por lo visual, las CA por calidad de código. El config completo tiene más de 60 reglas — usa las que necesites.

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

Si tu app maneja internacionalización o necesita una culture específica, el `web.config` debe declarar encoding y culture explícitamente. Sin esto, ASP.NET usa la culture del servidor — que en una fábrica en Tijuana probablemente no es la que quieres.

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

Este post cubre las secciones más útiles. El config completo tiene más de 300 líneas con todas las reglas de naming, formatting, y diagnostics de .NET.

Copia las secciones que necesites, o descarga el config completo desde el repositorio del proyecto. Lo importante es que VS y VS Code compartan el mismo `EditorConfig` — eso es lo que evita los diffs de formato que te vuelven loco en code review.
