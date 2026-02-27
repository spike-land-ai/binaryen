(module
  (import "env" "memory" (memory $0 256 256))
  (import "env" "table" (table $0 4 funcref))
  (import "env" "longname1" (func $internal1))
  (import "env" "longname2" (func $internal2))
  (import "env" "longname3" (func $internal3))
  (import "other" "longname4" (func $internal4))
)

(module
  (import "x" "a" (func $foo))
  (import "y" "a" (func $bar))
  (export "export1" (func $foo))
  (export "export2" (func $bar))
)
