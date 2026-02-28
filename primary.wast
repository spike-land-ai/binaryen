(module
 (global $foo (export "foo") (mut funcref) (ref.func $foo))
 (func $foo)
)