;; variable / constant with a docstring or comment block above it
;; TODO: Distinguish between class attributes and module-level constants
([(comment)+ (expression_statement (string))] @doc
 .
 (expression_statement
   (assignment
     left: (identifier) @name)) @definition

 (#strip! @doc "^\\s*#\\s*")
 (#select-adjacent! @doc @definition)) @documented

;; TODO: Module-level docstring

;; TODO: Class with a docstring

;; TODO: Function with a docstring or document comment block
;; TODO: Method with a docstring -- this differs from a function in that it needs the whole class body as context
([(comment)+ (expression_statement (string))] @doc
 .
 (expression_statement
   (assignment
     left: (identifier) @name)) @definition

 (#strip! @doc "^#\\s*")
 (#select-adjacent! @doc @definition)) @documented
