(module
 (import "import" "memory" (memory $memory 1 1))
 (func $foo (result i32)
  (i32.store (i32.const 1) (i32.const 1))
  (i32.const 1)
 )
 (export "foo" (func $foo))
)