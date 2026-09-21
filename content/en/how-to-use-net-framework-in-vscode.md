---
title: how to use net framework in vscode
slug: how-to-use-net-framework-in-vscode
tags:
  - dotnet
  - vscode
  - tools
created: '2025-11-26'
updated: '2025-11-26'
lang: en
lang_group: how-to-use-net-framework-in-vscode
---


## Language encoding in web.config
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
## Full Editor config

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

# C# files
[*.cs]

#### Core EditorConfig Options ####

# Indentation and spacing
indent_size = 4
indent_style = space
tab_width = 4

#### .NET Coding Conventions ####

# Organize usings
dotnet_sort_system_directives_first = true
dotnet_separate_import_directive_groups = false

# this. and Me. preferences
dotnet_style_qualification_for_field = false:warning
dotnet_style_qualification_for_property = false:warning
dotnet_style_qualification_for_method = false:warning
dotnet_style_qualification_for_event = false:warning

# Language keywords vs BCL types preferences
dotnet_style_predefined_type_for_locals_parameters_members = true:warning
dotnet_style_predefined_type_for_member_access = true:warning

# Parentheses preferences
dotnet_style_parentheses_in_arithmetic_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_relational_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_other_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_other_operators = never_if_unnecessary:suggestion

# Modifier preferences
dotnet_style_require_accessibility_modifiers = for_non_interface_members:warning
dotnet_style_readonly_field = true:warning

# Expression-level preferences
dotnet_style_object_initializer = true:suggestion
dotnet_style_collection_initializer = true:suggestion
dotnet_style_explicit_tuple_names = true:warning
dotnet_style_null_propagation = true:suggestion
dotnet_style_coalesce_expression = true:suggestion
dotnet_style_prefer_is_null_check_over_reference_equality_method = true:suggestion
dotnet_style_prefer_inferred_tuple_names = true:suggestion
dotnet_style_prefer_inferred_anonymous_type_member_names = true:suggestion
dotnet_style_prefer_auto_properties = true:suggestion
dotnet_style_prefer_conditional_expression_over_assignment = true:silent
dotnet_style_prefer_conditional_expression_over_return = true:silent
dotnet_style_prefer_compound_assignment = true:suggestion

#### C# Coding Conventions ####

# var preferences
csharp_style_var_for_built_in_types = true:suggestion
csharp_style_var_when_type_is_apparent = true:suggestion
csharp_style_var_elsewhere = true:suggestion

# Expression-bodied members
csharp_style_expression_bodied_methods = false:silent
csharp_style_expression_bodied_constructors = false:silent
csharp_style_expression_bodied_operators = false:silent
csharp_style_expression_bodied_properties = true:suggestion
csharp_style_expression_bodied_indexers = true:suggestion
csharp_style_expression_bodied_accessors = true:suggestion
csharp_style_expression_bodied_lambdas = true:suggestion
csharp_style_expression_bodied_local_functions = false:silent

# Pattern matching preferences
csharp_style_pattern_matching_over_is_with_cast_check = true:suggestion
csharp_style_pattern_matching_over_as_with_null_check = true:suggestion
csharp_style_prefer_switch_expression = true:suggestion
csharp_style_prefer_pattern_matching = true:silent
csharp_style_prefer_not_pattern = true:suggestion

# Null-checking preferences
csharp_style_throw_expression = true:suggestion
csharp_style_conditional_delegate_call = true:suggestion

# Modifier preferences
csharp_prefer_static_local_function = true:warning
csharp_preferred_modifier_order = public,private,protected,internal,static,extern,new,virtual,abstract,sealed,override,readonly,unsafe,volatile,async:suggestion

# Code-block preferences
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion

# Expression-level preferences
csharp_prefer_simple_default_expression = true:suggestion
csharp_style_pattern_local_over_anonymous_function = true:suggestion
csharp_style_inlined_variable_declaration = true:suggestion
csharp_style_deconstructed_variable_declaration = true:suggestion
csharp_style_prefer_index_operator = true:suggestion
csharp_style_prefer_range_operator = true:suggestion
csharp_style_implicit_object_creation_when_type_is_apparent = true:suggestion

# 'using' directive preferences
csharp_using_directive_placement = outside_namespace:warning

# Namespace preferences
csharp_style_namespace_declarations = file_scoped:warning

#### C# Formatting Rules ####

# New line preferences - EXPLICIT for VS and VS Code consistency
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
csharp_indent_block_contents = true
csharp_indent_braces = false
csharp_indent_case_contents_when_block = false

# Space preferences
csharp_space_after_cast = false
csharp_space_after_keywords_in_control_flow_statements = true
csharp_space_between_parentheses = false
csharp_space_before_colon_in_inheritance_clause = true
csharp_space_after_colon_in_inheritance_clause = true
csharp_space_around_binary_operators = before_and_after
csharp_space_between_method_declaration_parameter_list_parentheses = false
csharp_space_between_method_declaration_empty_parameter_list_parentheses = false
csharp_space_between_method_declaration_name_and_open_parenthesis = false
csharp_space_between_method_call_parameter_list_parentheses = false
csharp_space_between_method_call_empty_parameter_list_parentheses = false
csharp_space_between_method_call_name_and_opening_parenthesis = false
csharp_space_after_comma = true
csharp_space_before_comma = false
csharp_space_after_dot = false
csharp_space_before_dot = false
csharp_space_after_semicolon_in_for_statement = true
csharp_space_before_semicolon_in_for_statement = false
csharp_space_around_declaration_statements = false
csharp_space_before_open_square_brackets = false
csharp_space_between_empty_square_brackets = false
csharp_space_between_square_brackets = false

# Wrapping preferences
csharp_preserve_single_line_statements = false
csharp_preserve_single_line_blocks = true

#### Naming Conventions ####

# Naming rules

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

# Non-field members should be PascalCase
dotnet_naming_rule.non_field_members_should_be_pascal_case.severity = warning
dotnet_naming_rule.non_field_members_should_be_pascal_case.symbols = non_field_members
dotnet_naming_rule.non_field_members_should_be_pascal_case.style = pascal_case

dotnet_naming_symbols.non_field_members.applicable_kinds = property,event,method
dotnet_naming_symbols.non_field_members.applicable_accessibilities = *

# Private fields should be _camelCase
dotnet_naming_rule.private_fields_with_underscore.severity = warning
dotnet_naming_rule.private_fields_with_underscore.symbols = private_fields
dotnet_naming_rule.private_fields_with_underscore.style = prefix_underscore

dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private

dotnet_naming_style.prefix_underscore.required_prefix = _
dotnet_naming_style.prefix_underscore.capitalization = camel_case

# Public fields should be PascalCase
dotnet_naming_rule.public_fields_should_be_pascal_case.severity = warning
dotnet_naming_rule.public_fields_should_be_pascal_case.symbols = public_fields
dotnet_naming_rule.public_fields_should_be_pascal_case.style = pascal_case

dotnet_naming_symbols.public_fields.applicable_kinds = field
dotnet_naming_symbols.public_fields.applicable_accessibilities = public,internal,protected,protected_internal

# Constants should be PascalCase
dotnet_naming_rule.constants_should_be_pascal_case.severity = warning
dotnet_naming_rule.constants_should_be_pascal_case.symbols = constants
dotnet_naming_rule.constants_should_be_pascal_case.style = pascal_case

dotnet_naming_symbols.constants.applicable_kinds = field
dotnet_naming_symbols.constants.required_modifiers = const

# Local variables should be camelCase
dotnet_naming_rule.local_variables_should_be_camel_case.severity = suggestion
dotnet_naming_rule.local_variables_should_be_camel_case.symbols = local_variables
dotnet_naming_rule.local_variables_should_be_camel_case.style = camel_case

dotnet_naming_symbols.local_variables.applicable_kinds = local

dotnet_naming_style.camel_case.capitalization = camel_case

# Parameters should be camelCase
dotnet_naming_rule.parameters_should_be_camel_case.severity = warning
dotnet_naming_rule.parameters_should_be_camel_case.symbols = parameters
dotnet_naming_rule.parameters_should_be_camel_case.style = camel_case

dotnet_naming_symbols.parameters.applicable_kinds = parameter

#### Diagnostic Severities ####

# IDE diagnostics
dotnet_diagnostic.IDE0001.severity = warning # Simplify name
dotnet_diagnostic.IDE0002.severity = warning # Simplify member access
dotnet_diagnostic.IDE0003.severity = warning # Remove this or Me qualification
dotnet_diagnostic.IDE0004.severity = warning # Remove unnecessary cast
dotnet_diagnostic.IDE0005.severity = warning # Remove unnecessary import
dotnet_diagnostic.IDE0051.severity = warning # Remove unused private member
dotnet_diagnostic.IDE0052.severity = warning # Remove unread private member
dotnet_diagnostic.IDE0055.severity = warning # Fix formatting
dotnet_diagnostic.IDE0058.severity = silent # Expression value is never used
dotnet_diagnostic.IDE0059.severity = warning # Unnecessary assignment
dotnet_diagnostic.IDE0060.severity = warning # Remove unused parameter
dotnet_diagnostic.IDE0061.severity = warning # Use expression body for local functions
dotnet_diagnostic.IDE0062.severity = warning # Make local function static
dotnet_diagnostic.IDE0063.severity = warning # Use simple using statement
dotnet_diagnostic.IDE0064.severity = warning # Make struct fields writable
dotnet_diagnostic.IDE0065.severity = warning # using directive placement
dotnet_diagnostic.IDE0066.severity = warning # Use switch expression
dotnet_diagnostic.IDE1006.severity = warning # Naming rule violation

# Code quality rules
dotnet_diagnostic.CA1001.severity = warning # Types that own disposable fields should be disposable
dotnet_diagnostic.CA1009.severity = warning # Declare event handlers correctly
dotnet_diagnostic.CA1016.severity = warning # Mark assemblies with AssemblyVersionAttribute
dotnet_diagnostic.CA1033.severity = warning # Interface methods should be callable by child types
dotnet_diagnostic.CA1049.severity = warning # Types that own native resources should be disposable
dotnet_diagnostic.CA1060.severity = warning # Move P/Invokes to NativeMethods class
dotnet_diagnostic.CA1061.severity = warning # Do not hide base class methods
dotnet_diagnostic.CA1063.severity = warning # Implement IDisposable correctly
dotnet_diagnostic.CA1065.severity = warning # Do not raise exceptions in unexpected locations
dotnet_diagnostic.CA1301.severity = warning # Avoid duplicate accelerators
dotnet_diagnostic.CA1400.severity = warning # P/Invoke entry points should exist
dotnet_diagnostic.CA1401.severity = warning # P/Invokes should not be visible
dotnet_diagnostic.CA1403.severity = warning # Auto layout types should not be COM visible
dotnet_diagnostic.CA1404.severity = warning # Call GetLastError immediately after P/Invoke
dotnet_diagnostic.CA1405.severity = warning # COM visible type base types should be COM visible
dotnet_diagnostic.CA1410.severity = warning # COM registration methods should be matched
dotnet_diagnostic.CA1415.severity = warning # Declare P/Invokes correctly
dotnet_diagnostic.CA1821.severity = warning # Remove empty finalizers
dotnet_diagnostic.CA1900.severity = warning # Value type fields should be portable
dotnet_diagnostic.CA1901.severity = warning # P/Invoke declarations should be portable
dotnet_diagnostic.CA2002.severity = warning # Do not lock on objects with weak identity
dotnet_diagnostic.CA2100.severity = warning # Review SQL queries for security vulnerabilities
dotnet_diagnostic.CA2101.severity = warning # Specify marshaling for P/Invoke string arguments
dotnet_diagnostic.CA2108.severity = warning # Review declarative security on value types
dotnet_diagnostic.CA2111.severity = warning # Pointers should not be visible
dotnet_diagnostic.CA2112.severity = warning # Secured types should not expose fields
dotnet_diagnostic.CA2114.severity = warning # Method security should be a superset of type
dotnet_diagnostic.CA2116.severity = warning # APTCA methods should only call APTCA methods
dotnet_diagnostic.CA2117.severity = warning # APTCA types should only extend APTCA base types
dotnet_diagnostic.CA2122.severity = warning # Do not indirectly expose methods with link demands
dotnet_diagnostic.CA2123.severity = warning # Override link demands should be identical to base
dotnet_diagnostic.CA2124.severity = warning # Wrap vulnerable finally clauses in outer try
dotnet_diagnostic.CA2126.severity = warning # Type link demands require inheritance demands
dotnet_diagnostic.CA2131.severity = warning # Security critical types may not participate in type equivalence
dotnet_diagnostic.CA2132.severity = warning # Default constructors must be at least as critical as base type default constructors
dotnet_diagnostic.CA2133.severity = warning # Delegates must bind to methods with consistent transparency
dotnet_diagnostic.CA2134.severity = warning # Methods must keep consistent transparency when overriding base methods
dotnet_diagnostic.CA2137.severity = warning # Transparent methods must contain only verifiable IL
dotnet_diagnostic.CA2138.severity = warning # Transparent methods must not call methods with the SuppressUnmanagedCodeSecurity attribute
dotnet_diagnostic.CA2140.severity = warning # Transparent code must not reference security critical items
dotnet_diagnostic.CA2141.severity = warning # Transparent methods must not satisfy LinkDemands
dotnet_diagnostic.CA2146.severity = warning # Types must be at least as critical as their base types and interfaces
dotnet_diagnostic.CA2147.severity = warning # Transparent methods may not use security asserts
dotnet_diagnostic.CA2149.severity = warning # Transparent methods must not call into native code
dotnet_diagnostic.CA2200.severity = warning # Rethrow to preserve stack details
dotnet_diagnostic.CA2202.severity = warning # Do not dispose objects multiple times
dotnet_diagnostic.CA2207.severity = warning # Initialize value type static fields inline
dotnet_diagnostic.CA2212.severity = warning # Do not mark serviced components with WebMethod
dotnet_diagnostic.CA2213.severity = warning # Disposable fields should be disposed
dotnet_diagnostic.CA2214.severity = warning # Do not call overridable methods in constructors
dotnet_diagnostic.CA2216.severity = warning # Disposable types should declare finalizer
dotnet_diagnostic.CA2220.severity = warning # Finalizers should call base class finalizer
dotnet_diagnostic.CA2229.severity = warning # Implement serialization constructors
dotnet_diagnostic.CA2231.severity = warning # Overload operator equals on overriding ValueType.Equals
dotnet_diagnostic.CA2232.severity = warning # Mark Windows Forms entry points with STAThread
dotnet_diagnostic.CA2235.severity = warning # Mark all non-serializable fields
dotnet_diagnostic.CA2236.severity = warning # Call base class methods on ISerializable types
dotnet_diagnostic.CA2237.severity = warning # Mark ISerializable types with SerializableAttribute
dotnet_diagnostic.CA2238.severity = warning # Implement serialization methods correctly
dotnet_diagnostic.CA2240.severity = warning # Implement ISerializable correctly
dotnet_diagnostic.CA2241.severity = warning # Provide correct arguments to formatting methods
dotnet_diagnostic.CA2242.severity = warning # Test for NaN correctly
```
