{% macro none_to_empty(field) %}
  coalesce(nullif({{ field }}, 'none'), '')
{% endmacro %}
