((comment)* @doc
 .
 (module
  (expression_statement (assignment left: (identifier) @name) @definition.constant))
 (#strip! @doc "^#\\s*")
 (#select-adjacent! @doc @definition.constant)) @definition.constant.with-doc
