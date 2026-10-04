Refactor task: convert the module-level global state into a class
`SessionStore` with the same operations (create, close, active_count, plus
constructor starts empty). Keep thin module-level wrapper functions delegating
to a private store instance ONLY IF needed for backward compatibility — or
migrate fully to the class; either way the CLASS must exist and hold the
state, and module functions must not use `global` statements anymore.