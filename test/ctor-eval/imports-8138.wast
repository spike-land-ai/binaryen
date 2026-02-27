(module
 (import "env" "global" (global $global i32))
 (import "env" "global" (global $global1 i32))

 (func $foo (result i32)
  (i32.const 1)
 )
 (export "foo" (func $foo))
)