(module
 (type $f (func))
 (import "primary" "foo" (global $gimport$0 (mut funcref)))
 (func $bar (export "bar") (type $f)
  (return_call_ref $f
    (ref.cast (ref null $f)
      (global.get $gimport$0)
    )
  )
 )
)